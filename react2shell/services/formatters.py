"""Operation-specific report formatters for React2Shell."""

from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseFormatter:
    """Base formatter class for all operations."""
    
    def __init__(self, operation_type: str, description: str):
        self.operation_type = operation_type
        self.description = description
        self.title = operation_type.replace('_', ' ').title()
    
    def format_html_header(self, start_time: datetime, end_time: datetime, total_results: int) -> str:
        """Generate HTML header section."""
        duration = (end_time - start_time).total_seconds()
        return f"""
    <h1>React2Shell (R2S) - {self.title}</h1>
    <p class="description">{self.description}</p>
    <div class="metadata">
        <div class="metadata-item">
            <span class="metadata-label">Operation</span>
            <span class="metadata-value">{self.operation_type}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Start Time</span>
            <span class="metadata-value">{start_time.strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">End Time</span>
            <span class="metadata-value">{end_time.strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Duration</span>
            <span class="metadata-value">{duration:.2f}s</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Total Results</span>
            <span class="metadata-value">{total_results}</span>
        </div>
    </div>
    <hr>
"""
    
    def format_json_metadata(self, start_time: datetime, end_time: datetime, total_results: int) -> Dict[str, Any]:
        """Generate JSON metadata section."""
        return {
            'operation': self.operation_type,
            'title': self.title,
            'description': self.description,
            'scan_start': start_time.isoformat(),
            'scan_end': end_time.isoformat(),
            'total_results': total_results
        }
    
    def format_txt_header(self, start_time: datetime, end_time: datetime, total_results: int) -> str:
        """Generate text header section."""
        return f"""React2Shell (R2S) - {self.title}
{'=' * 60}

Description: {self.description}
Operation: {self.operation_type}
Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Total Results: {total_results}

{'-' * 60}

"""


class SecretsFormatter(BaseFormatter):
    """Formatter for secrets operation."""
    
    def __init__(self):
        super().__init__(
            "secrets",
            "Attempts to read application secrets and configuration files including .env files, config files, and sensitive data."
        )
        self.files_tried = []
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format secrets data for HTML."""
        html = """
    <h2>Files Attempted</h2>
    <ul>
"""
        for result in results:
            if result.get('type') == 'secrets' and result.get('data'):
                data = result.get('data', {})
                for file_path, content in data.items():
                    self.files_tried.append(file_path)
                    try:
                        html += f"""
        <li class="file-name">📄 {self._escape_html(file_path)}</li>
"""
                    except Exception:
                        html += f"""
        <li class="file-name">📄 {file_path}</li>
"""
        
        html += """
    </ul>
    <h2>Found Secrets</h2>
"""
        
        for result in results:
            if result.get('type') == 'secrets' and result.get('data'):
                data = result.get('data', {})
                for file_path, content in data.items():
                    try:
                        safe_file_id = self._escape_html(file_path).replace(' ', '-').replace('/', '-').replace('.', '-')
                        html += f"""
    <div class="data-section">
        <h3 class="file-name">📄 {self._escape_html(file_path)}</h3>
        <div class="copy-container">
            <button class="copy-btn" onclick="copyToClipboard('secret-{safe_file_id}')" title="Copy file content">
                📋 Copy
            </button>
        </div>
        <pre id="secret-{safe_file_id}"><code>{self._escape_html(str(content))}</code></pre>
    </div>
"""
                    except Exception:
                        html += f"""
    <div class="data-section">
        <h3 class="file-name">📄 {self._escape_html(str(file_path))}</h3>
        <div class="error-box">
            <strong>Error:</strong> Could not display content
        </div>
    </div>
"""
        
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format secrets data for text."""
        txt = "Files Attempted:\n"
        for result in results:
            if result.get('type') == 'secrets' and result.get('data'):
                data = result.get('data', {})
                for file_path in data.keys():
                    txt += f"  - {file_path}\n"
        
        txt += "\nFound Secrets:\n" + "=" * 60 + "\n\n"
        for result in results:
            if result.get('type') == 'secrets' and result.get('data'):
                data = result.get('data', {})
                for file_path, content in data.items():
                    try:
                        txt += f"File: {file_path}\n"
                        txt += f"{str(content)}\n"
                        txt += "\n" + "-" * 60 + "\n\n"
                    except Exception:
                        txt += f"File: {file_path}\n[Error displaying content]\n\n"
        
        return txt
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        try:
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        except Exception:
            return str(text)[:1000] if text else ""


class SystemInfoFormatter(BaseFormatter):
    """Formatter for system_info operation."""
    
    def __init__(self):
        super().__init__(
            "system_info",
            "Gathers system information including OS version, hostname, current user, and environment variables."
        )
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format system info data for HTML."""
        html = "<h2>System Information</h2>\n"
        for result in results:
            if result.get('type') == 'system_info' and result.get('data'):
                data = result.get('data', {})
                for name, value in data.items():
                    try:
                        value_str = str(value)
                        safe_name_id = self._escape_html(name).replace(' ', '-').lower()
                        html += f"""
        <div class="data-section">
            <h4>{self._escape_html(name)}</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('sysinfo-{safe_name_id}')" title="Copy {self._escape_html(name)}">
                    📋 Copy
                </button>
            </div>
            <pre id="sysinfo-{safe_name_id}"><code>{self._escape_html(value_str)}</code></pre>
        </div>
"""
                    except Exception as e:
                        html += f"""
        <div class="data-section">
            <h4>{self._escape_html(str(name))}</h4>
            <div class="error-box">
                <strong>Error:</strong> Could not display data - {self._escape_html(str(e))}
            </div>
        </div>
"""
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format system info data for text."""
        txt = "System Information:\n" + "=" * 60 + "\n\n"
        for result in results:
            if result.get('type') == 'system_info' and result.get('data'):
                data = result.get('data', {})
                for name, value in data.items():
                    try:
                        txt += f"{name}:\n{str(value)}\n\n" + "-" * 60 + "\n\n"
                    except Exception:
                        txt += f"{name}:\n[Error displaying data]\n\n"
        return txt
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        try:
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        except Exception:
            return str(text)[:1000] if text else ""


class CodeFormatter(BaseFormatter):
    """Formatter for code operation."""
    
    def __init__(self):
        super().__init__(
            "code",
            "Attempts to read application source code files including TypeScript, JavaScript, and configuration files."
        )
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format code data for HTML."""
        html = """
    <h2>Files Attempted</h2>
    <ul>
"""
        for result in results:
            if result.get('type') == 'code' and result.get('data'):
                data = result.get('data', {})
                for file_path in data.keys():
                    try:
                        html += f"""
        <li class="file-name">📄 {self._escape_html(file_path)}</li>
"""
                    except Exception:
                        html += f"""
        <li class="file-name">📄 {file_path}</li>
"""
        
        html += """
    </ul>
    <h2>Found Code</h2>
"""
        
        for result in results:
            if result.get('type') == 'code' and result.get('data'):
                data = result.get('data', {})
                for file_path, content in data.items():
                    try:
                        safe_file_id = self._escape_html(file_path).replace(' ', '-').replace('/', '-').replace('.', '-')
                        html += f"""
    <div class="data-section">
        <h3 class="file-name">📄 {self._escape_html(file_path)}</h3>
        <div class="copy-container">
            <button class="copy-btn" onclick="copyToClipboard('code-{safe_file_id}')" title="Copy file content">
                📋 Copy
            </button>
        </div>
        <pre id="code-{safe_file_id}"><code>{self._escape_html(str(content))}</code></pre>
    </div>
"""
                    except Exception:
                        html += f"""
    <div class="data-section">
        <h3 class="file-name">📄 {self._escape_html(str(file_path))}</h3>
        <div class="error-box">
            <strong>Error:</strong> Could not display content
        </div>
    </div>
"""
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format code data for text."""
        txt = "Files Attempted:\n"
        for result in results:
            if result.get('type') == 'code' and result.get('data'):
                data = result.get('data', {})
                for file_path in data.keys():
                    txt += f"  - {file_path}\n"
        
        txt += "\nFound Code:\n" + "=" * 60 + "\n\n"
        for result in results:
            if result.get('type') == 'code' and result.get('data'):
                data = result.get('data', {})
                for file_path, content in data.items():
                    try:
                        txt += f"File: {file_path}\n"
                        txt += f"{str(content)}\n"
                        txt += "\n" + "-" * 60 + "\n\n"
                    except Exception:
                        txt += f"File: {file_path}\n[Error displaying content]\n\n"
        return txt
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        try:
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        except Exception:
            return str(text)[:1000] if text else ""


class ModuleFormatter(BaseFormatter):
    """Formatter for exploit module results."""
    
    def __init__(self):
        super().__init__("module", "Exploit Module Execution Results")
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format module results for HTML."""
        html = ""
        for result in results:
            module_name = result.get('module_name', 'unknown')
            description = result.get('description', '')
            output = result.get('output', '')
            env_vars = result.get('environment_variables', {})
            
            html += f"""
    <div class="result">
        <h3>Module: {self._escape_html(module_name)}</h3>
        {f'<p class="description">{self._escape_html(description)}</p>' if description else ''}
"""
            
            # Format environment variables in a table if available
            if env_vars:
                html += """
        <div class="data-section">
            <h4>Environment Variables</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('env-vars')" title="Copy all environment variables">
                    📋 Copy All
                </button>
            </div>
            <table id="env-vars">
                <thead>
                    <tr>
                        <th>Variable</th>
                        <th>Value</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
"""
                for key, value in sorted(env_vars.items()):
                    safe_key = self._escape_html(str(key))
                    safe_value = self._escape_html(str(value))
                    html += f"""
                    <tr>
                        <td><code>{safe_key}</code></td>
                        <td><code class="copyable" data-value="{safe_value}">{safe_value}</code></td>
                        <td>
                            <button class="copy-btn-small" onclick="copyToClipboard('{safe_value.replace("'", "\\'")}')" title="Copy value">
                                📋
                            </button>
                        </td>
                    </tr>
"""
                html += """
                </tbody>
            </table>
        </div>
"""
            elif output:
                html += f"""
        <div class="data-section">
            <h4>Output</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('module-output')" title="Copy output">
                    📋 Copy
                </button>
            </div>
            <pre id="module-output"><code>{self._escape_html(output)}</code></pre>
        </div>
"""
            
            html += """
    </div>
"""
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format module results for text."""
        txt = ""
        for result in results:
            module_name = result.get('module_name', 'unknown')
            description = result.get('description', '')
            output = result.get('output', '')
            env_vars = result.get('environment_variables', {})
            
            txt += f"\nModule: {module_name}\n"
            if description:
                txt += f"Description: {description}\n"
            txt += "\n"
            
            if env_vars:
                txt += "Environment Variables:\n"
                txt += "-" * 60 + "\n"
                for key, value in sorted(env_vars.items()):
                    txt += f"{key}={value}\n"
                txt += "\n"
            elif output:
                txt += "Output:\n"
                txt += "-" * 60 + "\n"
                txt += f"{output}\n\n"
        
        return txt


class ExportFormatter(BaseFormatter):
    """Formatter for export operation results."""
    
    def __init__(self):
        super().__init__(
            "export",
            "Exports files or entire application directory from the target server."
        )
    
    def _build_tree_structure(self, files: List) -> Dict:
        """Build a hierarchical tree structure from file paths."""
        tree = {}
        
        for file_item in files:
            if isinstance(file_item, dict):
                path = file_item.get('relative_path') or file_item.get('path', '')
            else:
                path = str(file_item)
            
            if not path:
                continue
            
            # Normalize path separators
            path = path.replace('\\', '/')
            # Remove leading slashes
            path = path.lstrip('/')
            
            if not path:
                continue
            
            parts = [p for p in path.split('/') if p]
            if not parts:
                continue
            
            current = tree
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        return tree
    
    def _format_tree_html(self, tree: Dict, prefix: str = "", is_last: bool = True, depth: int = 0, max_depth: int = 10) -> str:
        """Format tree structure as HTML with tree characters."""
        if depth > max_depth:
            return ""
        
        html = ""
        items = sorted(tree.items())
        
        for i, (name, children) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            is_dir = bool(children)
            
            connector = "└── " if is_last_item else "├── "
            
            if is_dir:
                name_html = f'<span class="tree-dir">{self._escape_html(name)}/</span>'
            else:
                name_html = f'<span class="tree-file">{self._escape_html(name)}</span>'
            
            html += f'<div class="tree-line"><span class="tree-connector">{self._escape_html(prefix)}{connector}</span>{name_html}</div>'
            
            if children:
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                html += self._format_tree_html(children, next_prefix, is_last_item, depth + 1, max_depth)
        
        return html
    
    def _format_tree_txt(self, tree: Dict, prefix: str = "", is_last: bool = True, depth: int = 0, max_depth: int = 10) -> str:
        """Format tree structure as text with tree characters."""
        if depth > max_depth:
            return ""
        
        txt = ""
        items = sorted(tree.items())
        
        for i, (name, children) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            is_dir = bool(children)
            
            connector = "└── " if is_last_item else "├── "
            name_display = f"{name}/" if is_dir else name
            
            txt += f"{prefix}{connector}{name_display}\n"
            
            if children:
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                txt += self._format_tree_txt(children, next_prefix, is_last_item, depth + 1, max_depth)
        
        return txt
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format export data for HTML."""
        html = ""
        for result in results:
            if result.get('type') == 'export' and result.get('data'):
                data = result.get('data', {})
                export_type = data.get('type', 'file')
                
                if export_type == 'file':
                    file_path = data.get('file_path', 'Unknown')
                    metadata = data.get('metadata', {})
                    
                    html += """
    <div class="result">
        <h2>📄 File Export</h2>
        <div class="data-section">
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">File Path:</span>
                    <span class="info-value">
                        <code class="file-path">{}</code>
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">Size:</span>
                    <span class="info-value">{}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Lines:</span>
                    <span class="info-value">{}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Characters:</span>
                    <span class="info-value">{}</span>
                </div>
            </div>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('export-path')" title="Copy file path">
                    📋 Copy Path
                </button>
            </div>
            <pre id="export-path" style="display: none;">{}</pre>
        </div>
    </div>
""".format(
                        self._escape_html(file_path),
                        self._format_bytes(metadata.get('size', 0)),
                        metadata.get('lines', 0),
                        metadata.get('chars', 0),
                        self._escape_html(file_path)
                    )
                
                elif export_type == 'archive':
                    archive_path = data.get('archive_path', 'Unknown')
                    metadata = data.get('metadata', {})
                    files = data.get('files', [])
                    
                    html += """
    <div class="result">
        <h2>📦 Archive Export</h2>
        <div class="data-section">
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Archive Path:</span>
                    <span class="info-value">
                        <code class="file-path">{}</code>
                    </span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Files:</span>
                    <span class="info-value">{}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Size:</span>
                    <span class="info-value">{}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Lines:</span>
                    <span class="info-value">{}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Characters:</span>
                    <span class="info-value">{}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">File Extensions:</span>
                    <span class="info-value">{}</span>
                </div>
            </div>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('archive-path')" title="Copy archive path">
                    📋 Copy Path
                </button>
            </div>
            <pre id="archive-path" style="display: none;">{}</pre>
""".format(
                        self._escape_html(archive_path),
                        metadata.get('total_files', 0),
                        self._format_bytes(metadata.get('total_size', 0)),
                        metadata.get('total_lines', 0),
                        metadata.get('total_chars', 0),
                        len(metadata.get('extensions', {})),
                        self._escape_html(archive_path)
                    )
                    
                    if metadata.get('extensions'):
                        html += """
            <h3>File Types</h3>
            <div class="extensions-grid">
"""
                        for ext, count in sorted(metadata['extensions'].items(), key=lambda x: x[1], reverse=True):
                            html += f"""
                <div class="extension-item">
                    <span class="extension-name">{self._escape_html(ext or 'no extension')}</span>
                    <span class="extension-count">{count} files</span>
                </div>
"""
                        html += """
            </div>
"""
                    
                    if files:
                        tree_structure = self._build_tree_structure(files)
                        tree_text = self._format_tree_txt(tree_structure)
                        tree_html = self._format_tree_html(tree_structure)
                        
                        html += """
            <h3>Directory Tree</h3>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('file-tree-text')" title="Copy file tree">
                    📋 Copy Tree
                </button>
            </div>
            <div class="file-tree" id="file-tree">
"""
                        html += tree_html
                        html += f"""
            </div>
            <pre id="file-tree-text" style="display: none;">{self._escape_html(tree_text)}</pre>
"""
                    
                    html += """
        </div>
    </div>
"""
                else:
                    html += f"""
    <div class="result">
        <h2>Export Result</h2>
        <div class="error-box">
            <strong>Error:</strong> Unknown export type
        </div>
    </div>
"""
            elif result.get('type') == 'export' and not result.get('success', True):
                error = result.get('error', 'Unknown error')
                html += f"""
    <div class="result">
        <h2>❌ Export Failed</h2>
        <div class="error-box">
            <strong>Error:</strong> {self._escape_html(str(error))}
        </div>
    </div>
"""
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format export data for text."""
        txt = ""
        for result in results:
            if result.get('type') == 'export' and result.get('data'):
                data = result.get('data', {})
                export_type = data.get('type', 'file')
                
                if export_type == 'file':
                    file_path = data.get('file_path', 'Unknown')
                    metadata = data.get('metadata', {})
                    
                    txt += "File Export:\n"
                    txt += "=" * 60 + "\n"
                    txt += f"File Path: {file_path}\n"
                    txt += f"Size: {self._format_bytes(metadata.get('size', 0))}\n"
                    txt += f"Lines: {metadata.get('lines', 0)}\n"
                    txt += f"Characters: {metadata.get('chars', 0)}\n"
                    txt += "\n"
                
                elif export_type == 'archive':
                    archive_path = data.get('archive_path', 'Unknown')
                    metadata = data.get('metadata', {})
                    files = data.get('files', [])
                    
                    txt += "Archive Export:\n"
                    txt += "=" * 60 + "\n"
                    txt += f"Archive Path: {archive_path}\n"
                    txt += f"Total Files: {metadata.get('total_files', 0)}\n"
                    txt += f"Total Size: {self._format_bytes(metadata.get('total_size', 0))}\n"
                    txt += f"Total Lines: {metadata.get('total_lines', 0)}\n"
                    txt += f"Total Characters: {metadata.get('total_chars', 0)}\n"
                    txt += f"File Extensions: {len(metadata.get('extensions', {}))}\n"
                    txt += "\n"
                    
                    if metadata.get('extensions'):
                        txt += "File Types:\n"
                        txt += "-" * 60 + "\n"
                        for ext, count in sorted(metadata['extensions'].items(), key=lambda x: x[1], reverse=True):
                            txt += f"  {ext or 'no extension'}: {count} files\n"
                        txt += "\n"
                    
                    if files:
                        txt += "Directory Tree:\n"
                        txt += "=" * 60 + "\n"
                        tree_structure = self._build_tree_structure(files)
                        txt += self._format_tree_txt(tree_structure)
                        txt += "\n"
            
            elif result.get('type') == 'export' and not result.get('success', True):
                error = result.get('error', 'Unknown error')
                txt += "Export Failed:\n"
                txt += "=" * 60 + "\n"
                txt += f"Error: {error}\n\n"
        
        return txt
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} TB"
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        try:
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        except Exception:
            return str(text)[:1000] if text else ""


class ModuleFormatter(BaseFormatter):
    """Formatter for exploit module results."""
    
    def __init__(self):
        super().__init__("module", "Exploit Module Execution Results")
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format module results for HTML."""
        html = ""
        for result in results:
            module_name = result.get('module_name', 'unknown')
            description = result.get('description', '')
            output = result.get('output', '')
            env_vars = result.get('environment_variables', {})
            
            html += f"""
    <div class="result">
        <h3>Module: {self._escape_html(module_name)}</h3>
        {f'<p class="description">{self._escape_html(description)}</p>' if description else ''}
"""
            
            # Format environment variables in a table if available
            if env_vars:
                html += """
        <div class="data-section">
            <h4>Environment Variables</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('env-vars')" title="Copy all environment variables">
                    📋 Copy All
                </button>
            </div>
            <table id="env-vars">
                <thead>
                    <tr>
                        <th>Variable</th>
                        <th>Value</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
"""
                for key, value in sorted(env_vars.items()):
                    safe_key = self._escape_html(str(key))
                    safe_value = self._escape_html(str(value))
                    html += f"""
                    <tr>
                        <td><code>{safe_key}</code></td>
                        <td><code class="copyable" data-value="{safe_value}">{safe_value}</code></td>
                        <td>
                            <button class="copy-btn-small" onclick="copyToClipboard('{safe_value.replace("'", "\\'")}')" title="Copy value">
                                📋
                            </button>
                        </td>
                    </tr>
"""
                html += """
                </tbody>
            </table>
        </div>
"""
            elif output:
                html += f"""
        <div class="data-section">
            <h4>Output</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('module-output')" title="Copy output">
                    📋 Copy
                </button>
            </div>
            <pre id="module-output"><code>{self._escape_html(output)}</code></pre>
        </div>
"""
            
            html += """
    </div>
"""
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format module results for text."""
        txt = ""
        for result in results:
            module_name = result.get('module_name', 'unknown')
            description = result.get('description', '')
            output = result.get('output', '')
            env_vars = result.get('environment_variables', {})
            
            txt += f"\nModule: {module_name}\n"
            if description:
                txt += f"Description: {description}\n"
            txt += "\n"
            
            if env_vars:
                txt += "Environment Variables:\n"
                txt += "-" * 60 + "\n"
                for key, value in sorted(env_vars.items()):
                    txt += f"{key}={value}\n"
                txt += "\n"
            elif output:
                txt += "Output:\n"
                txt += "-" * 60 + "\n"
                txt += f"{output}\n\n"
        
        return txt
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        try:
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        except Exception:
            return str(text)[:1000] if text else ""


class GenericFormatter(BaseFormatter):
    """Generic formatter for operations without specific formatters."""
    
    def __init__(self, operation_type: str, description: str = ""):
        if not description:
            description = f"Operation: {operation_type.replace('_', ' ').title()}"
        super().__init__(operation_type, description)
    
    def format_html_content(self, results: List[Dict[str, Any]]) -> str:
        """Format generic results for HTML."""
        html = ""
        for result in results:
            result_type = result.get('type', 'command')
            
            if result_type == 'shell_command' or result.get('command'):
                status_class = "vulnerable" if result.get("success") else "safe"
                status_text = "SUCCESS" if result.get("success") else "FAILED"
                
                html += f"""
    <div class="result">
        <p class="timestamp">{self._escape_html(result.get('timestamp', 'Unknown'))}</p>
        <p>Command: <span class="command">{self._escape_html(result.get('command', 'N/A'))}</span></p>
        <p>Status: <span class="{status_class}">{status_text}</span></p>
"""
                if result.get("output"):
                    html += f"""
        <h4>Output:</h4>
        <pre>{self._escape_html(result.get('output'))}</pre>
"""
                if result.get("error"):
                    html += f"""
        <p style="color: #f48771;">Error: {self._escape_html(result.get('error'))}</p>
"""
                html += """
    </div>
"""
            else:
                html += f"""
    <div class="result">
        <p class="timestamp">{self._escape_html(result.get('timestamp', 'Unknown'))}</p>
"""
                for key, value in result.items():
                    if key not in ['timestamp', 'type']:
                        try:
                            html += f"""
        <p><strong>{self._escape_html(str(key))}:</strong> {self._escape_html(str(value))[:500]}</p>
"""
                        except Exception:
                            pass
                html += """
    </div>
"""
        return html
    
    def format_txt_content(self, results: List[Dict[str, Any]]) -> str:
        """Format generic results for text."""
        txt = ""
        for result in results:
            try:
                result_type = result.get('type', 'command')
                txt += f"Time: {result.get('timestamp', 'Unknown')}\n"
                txt += f"Type: {result_type}\n"
                
                if result.get('command'):
                    txt += f"Command: {result.get('command', 'N/A')}\n"
                    txt += f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}\n"
                    if result.get('output'):
                        txt += f"Output:\n{result.get('output')}\n"
                    if result.get('error'):
                        txt += f"Error: {result.get('error')}\n"
                
                elif result.get('data'):
                    data = result.get('data', {})
                    if isinstance(data, dict):
                        txt += f"Status: {'SUCCESS' if result.get('success') else 'FAILED'}\n"
                        txt += f"Data:\n"
                        for key, value in data.items():
                            try:
                                txt += f"  {key}:\n"
                                txt += f"    {str(value)[:2000]}\n"
                            except Exception:
                                txt += f"  {key}: [Error displaying data]\n"
                
                txt += "\n" + "-" * 60 + "\n\n"
            except Exception:
                txt += f"[Error displaying result]\n\n"
        return txt
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        try:
            return (str(text)
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
        except Exception:
            return str(text)[:1000] if text else ""


def get_formatter(operation_type: str) -> BaseFormatter:
    """Get the appropriate formatter for an operation type."""
    formatters = {
        'secrets': SecretsFormatter,
        'system_info': SystemInfoFormatter,
        'code': CodeFormatter,
        'export': ExportFormatter,
    }
    
    formatter_class = formatters.get(operation_type)
    if formatter_class:
        return formatter_class()
    
    # Default descriptions for operations
    descriptions = {
        'test': 'Tests for CVE-2025-55182 vulnerability by attempting to execute a test command.',
        'shell': 'Interactive shell session for executing commands on the target server.',
        'list_directory': 'Lists directory contents on the target server.',
        'read_file': 'Reads file contents from the target server.',
        'custom_command': 'Executes a custom command on the target server.',
        'secrets': 'Attempts to read application secrets and configuration files including .env files, config files, and sensitive data.',
        'system_info': 'Gathers system information including OS version, hostname, current user, and environment variables.',
        'code': 'Attempts to read application source code files including TypeScript, JavaScript, and configuration files.',
        'export': 'Exports files or entire application directory from the target server.',
        'module': 'Executes exploit modules for specialized operations.',
    }
    
    description = descriptions.get(operation_type, f"Operation: {operation_type.replace('_', ' ').title()}")
    return GenericFormatter(operation_type, description)

