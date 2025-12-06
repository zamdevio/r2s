"""Reporting service for React2Shell."""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from .formatters import get_formatter


class Reporter:
    """Generate reports from scan results."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        self.operation_type = "scan"
    
    def set_operation(self, operation: str):
        """Set the operation type (shell, test, etc.)."""
        self.operation_type = operation
    
    def add_result(self, result: Dict[str, Any]):
        """Add a result to the report."""
        from ..utils.helpers import strip_ansi_codes
        
        if 'output' in result and result['output']:
            result['output'] = strip_ansi_codes(str(result['output']))
        if 'error' in result and result.get('error'):
            result['error'] = strip_ansi_codes(str(result['error']))
        
        result['timestamp'] = datetime.now().isoformat()
        self.results.append(result)
    
    def add_shell_command(self, command: str, output: str, success: bool, error: Optional[str] = None):
        """Add a shell command to the report."""
        from ..utils.helpers import strip_ansi_codes
        clean_output = strip_ansi_codes(output) if output else ""
        clean_error = strip_ansi_codes(error) if error else None
        
        self.add_result({
            'command': command,
            'output': clean_output,
            'success': success,
            'error': clean_error,
            'type': 'shell_command'
        })
    
    def add_operation_data(self, operation_type: str, data: Dict[str, Any]):
        """Add operation-specific data (secrets, system_info, code, etc.)."""
        from ..utils.helpers import strip_ansi_codes
        
        def clean_data(obj):
            """Recursively clean ANSI codes from data structures."""
            if isinstance(obj, str):
                return strip_ansi_codes(obj)
            elif isinstance(obj, dict):
                return {k: clean_data(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_data(item) for item in obj]
            return obj
        
        cleaned_data = clean_data(data)
        
        self.add_result({
            'type': operation_type,
            'data': cleaned_data,
            'success': bool(data),
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_quick_copy_section(self) -> str:
        """Generate quick copy section for important results."""
        important_data = []
        
        # Extract important data based on operation type
        if self.operation_type == "secrets":
            for result in self.results:
                if result.get('type') == 'secrets' and result.get('data'):
                    for file_path, content in result.get('data', {}).items():
                        important_data.append({
                            'label': f"Secret: {file_path}",
                            'value': str(content),
                            'id': f'quick-secret-{len(important_data)}'
                        })
        
        elif self.operation_type == "system_info":
            for result in self.results:
                if result.get('type') == 'system_info' and result.get('data'):
                    data = result.get('data', {})
                    # Prioritize environment variables
                    if 'Environment Variables' in data:
                        important_data.append({
                            'label': "Environment Variables",
                            'value': str(data['Environment Variables']),
                            'id': 'quick-env-vars'
                        })
        
        elif self.operation_type == "module":
            for result in self.results:
                env_vars = result.get('environment_variables', {})
                if env_vars:
                    # Format as KEY=VALUE
                    env_str = '\n'.join([f"{k}={v}" for k, v in sorted(env_vars.items())])
                    important_data.append({
                        'label': "Module: Environment Variables",
                        'value': env_str,
                        'id': 'quick-module-env'
                    })
        
        if not important_data:
            return ""
        
        html = """
    <hr>
    <div class="result" style="background: var(--bg-secondary); border: 2px solid var(--accent-color);">
        <h2>📋 Quick Copy - Important Results</h2>
        <p class="description">One-click copy for important findings</p>
"""
        for item in important_data:
            safe_value = self._escape_html_for_report(item['value'])
            html += f"""
        <div class="data-section" style="margin: 10px 0;">
            <h4>{self._escape_html_for_report(item['label'])}</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('{item['id']}')" title="Copy {self._escape_html_for_report(item['label'])}">
                    📋 Copy
                </button>
            </div>
            <pre id="{item['id']}" style="max-height: 200px; overflow-y: auto;"><code>{safe_value[:1000]}{'...' if len(item['value']) > 1000 else ''}</code></pre>
        </div>
"""
        html += """
    </div>
"""
        return html
    
    def _escape_html_for_report(self, text: str) -> str:
        """Escape HTML special characters for reports."""
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
    
    def _generate_quick_copy_section(self) -> str:
        """Generate quick copy section for important results."""
        important_data = []
        
        # Extract important data based on operation type
        if self.operation_type == "secrets":
            for result in self.results:
                if result.get('type') == 'secrets' and result.get('data'):
                    for file_path, content in result.get('data', {}).items():
                        important_data.append({
                            'label': f"Secret: {file_path}",
                            'value': str(content),
                            'id': f'quick-secret-{len(important_data)}'
                        })
        
        elif self.operation_type == "system_info":
            for result in self.results:
                if result.get('type') == 'system_info' and result.get('data'):
                    data = result.get('data', {})
                    # Prioritize environment variables
                    if 'Environment Variables' in data:
                        important_data.append({
                            'label': "Environment Variables",
                            'value': str(data['Environment Variables']),
                            'id': 'quick-env-vars'
                        })
        
        elif self.operation_type == "module":
            for result in self.results:
                env_vars = result.get('environment_variables', {})
                if env_vars:
                    # Format as KEY=VALUE
                    env_str = '\n'.join([f"{k}={v}" for k, v in sorted(env_vars.items())])
                    important_data.append({
                        'label': "Module: Environment Variables",
                        'value': env_str,
                        'id': 'quick-module-env'
                    })
        
        if not important_data:
            return ""
        
        html = """
    <hr>
    <div class="result" style="background: var(--bg-secondary); border: 2px solid var(--accent-color);">
        <h2>📋 Quick Copy - Important Results</h2>
        <p class="description">One-click copy for important findings</p>
"""
        for item in important_data:
            safe_value = self._escape_html_for_report(item['value'])
            html += f"""
        <div class="data-section" style="margin: 10px 0;">
            <h4>{self._escape_html_for_report(item['label'])}</h4>
            <div class="copy-container">
                <button class="copy-btn" onclick="copyToClipboard('{item['id']}')" title="Copy {self._escape_html_for_report(item['label'])}">
                    📋 Copy
                </button>
            </div>
            <pre id="{item['id']}" style="max-height: 200px; overflow-y: auto;"><code>{safe_value[:1000]}{'...' if len(item['value']) > 1000 else ''}</code></pre>
        </div>
"""
        html += """
    </div>
"""
        return html
    
    def _escape_html_for_report(self, text: str) -> str:
        """Escape HTML special characters for reports."""
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
    
    def _safe_json_value(self, value: Any) -> Any:
        """Convert value to JSON-safe format, handling errors."""
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, dict):
                return {k: self._safe_json_value(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                return [self._safe_json_value(item) for item in value]
            else:
                return str(value)[:10000]  # Truncate very long values
        except Exception:
            return str(value)[:1000] if value else None
    
    def export_json(self, filename: str):
        """Export results to JSON file with error handling."""
        try:
            formatter = get_formatter(self.operation_type)
            safe_results = [self._safe_json_value(r) for r in self.results]
            end_time = datetime.now()
            
            report = formatter.format_json_metadata(self.start_time, end_time, len(safe_results))
            report['results'] = safe_results
            
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        except Exception as e:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'operation': self.operation_type,
                    'error': f'Failed to generate full report: {str(e)}',
                    'total_results': len(self.results)
                }, f, indent=2)
    
    def export_html(self, filename: str):
        """Export results to HTML file with operation-specific formatting."""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        try:
            formatter = get_formatter(self.operation_type)
            end_time = datetime.now()
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>R2S {formatter.title} Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; }}
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #0d1117;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --border-color: #30363d;
            --accent-color: #58a6ff;
            --success-color: #56d364;
            --error-color: #f85149;
        }}
        [data-theme="light"] {{
            --bg-primary: #ffffff;
            --bg-secondary: #f6f8fa;
            --bg-tertiary: #ffffff;
            --text-primary: #24292f;
            --text-secondary: #57606a;
            --border-color: #d0d7de;
            --accent-color: #0969da;
            --success-color: #1a7f37;
            --error-color: #cf222e;
        }}
        body {{ 
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace, Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: var(--bg-primary); 
            color: var(--text-primary); 
            line-height: 1.6;
            transition: background 0.3s, color 0.3s;
        }}
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            z-index: 1000;
            transition: all 0.3s;
        }}
        .theme-toggle:hover {{
            background: var(--bg-tertiary);
            border-color: var(--accent-color);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-secondary);
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: background 0.3s;
        }}
        h1 {{ 
            color: var(--accent-color); 
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{ 
            color: var(--accent-color); 
            margin-top: 30px; 
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}
        h3 {{ 
            color: var(--accent-color); 
            margin-top: 20px; 
        }}
        h4 {{ 
            color: var(--success-color); 
            margin-top: 15px; 
        }}
        .vulnerable {{ 
            color: var(--error-color); 
            font-weight: bold; 
            background: rgba(248, 81, 73, 0.1);
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .safe {{ 
            color: var(--success-color); 
            font-weight: bold;
            background: rgba(86, 211, 100, 0.1);
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .result {{
            background: var(--bg-tertiary); 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 6px; 
            border-left: 4px solid var(--accent-color);
            border: 1px solid var(--border-color);
            transition: all 0.3s;
        }}
        .result:hover {{
            border-color: var(--accent-color);
            box-shadow: 0 2px 8px rgba(88, 166, 255, 0.2);
        }}
        .timestamp {{ 
            color: var(--text-secondary); 
            font-size: 0.85em; 
            font-style: italic;
        }}
        .description {{ 
            color: var(--text-secondary); 
            font-style: italic; 
            margin: 10px 0; 
            padding: 10px;
            background: var(--bg-tertiary);
            border-left: 3px solid var(--accent-color);
            border-radius: 4px;
        }}
        pre, code {{
            background: var(--bg-tertiary);
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid var(--border-color);
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            position: relative;
        }}
        code {{
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.85em;
        }}
        pre code {{
            padding: 0;
            border: none;
            background: transparent;
        }}
        .command {{ 
            color: var(--accent-color); 
            font-weight: bold; 
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        .file-name {{ 
            color: var(--error-color); 
            font-weight: bold; 
        }}
        .data-section {{
            margin: 15px 0; 
            padding: 15px; 
            background: var(--bg-tertiary); 
            border-radius: 6px;
            border: 1px solid var(--border-color);
            transition: all 0.3s;
        }}
        .data-section:hover {{
            border-color: var(--accent-color);
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0; 
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid var(--border-color); 
        }}
        th {{
            color: var(--accent-color); 
            font-weight: bold; 
            background: var(--bg-secondary);
        }}
        tr:hover {{
            background: var(--bg-secondary);
        }}
        ul {{ 
            list-style-type: none; 
            padding-left: 0; 
        }}
        li {{ 
            padding: 8px 0; 
            border-bottom: 1px solid #30363d;
        }}
        li:last-child {{
            border-bottom: none;
        }}
        .error-box {{
            background: rgba(248, 81, 73, 0.1);
            border-left: 4px solid #f85149;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            color: #f85149;
        }}
        .success-box {{
            background: rgba(86, 211, 100, 0.1);
            border-left: 4px solid #56d364;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            color: #56d364;
        }}
        .info-box {{
            background: rgba(88, 166, 255, 0.1);
            border-left: 4px solid #58a6ff;
            padding: 12px;
            margin: 10px 0;
            border-radius: 4px;
            color: #58a6ff;
        }}
        hr {{
            border: none;
            border-top: 1px solid #30363d;
            margin: 20px 0;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
            padding: 15px;
            background: var(--bg-tertiary);
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}
        .metadata-item {{
            display: flex;
            flex-direction: column;
        }}
        .metadata-label {{
            color: var(--text-secondary);
            font-size: 0.85em;
            margin-bottom: 5px;
        }}
        .metadata-value {{
            color: var(--text-primary);
            font-weight: bold;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .info-item {{
            display: flex;
            flex-direction: column;
            padding: 12px;
            background: var(--bg-secondary);
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}
        .info-label {{
            color: var(--text-secondary);
            font-size: 0.85em;
            margin-bottom: 5px;
            font-weight: 600;
        }}
        .info-value {{
            color: var(--text-primary);
            font-size: 0.95em;
            word-break: break-word;
        }}
        .file-path {{
            color: var(--accent-color);
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            word-break: break-all;
        }}
        .extensions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .extension-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: var(--bg-secondary);
            border-radius: 6px;
            border: 1px solid var(--border-color);
            transition: all 0.2s;
        }}
        .extension-item:hover {{
            border-color: var(--accent-color);
            background: var(--bg-tertiary);
        }}
        .extension-name {{
            color: var(--text-primary);
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .extension-count {{
            color: var(--text-secondary);
            font-size: 0.85em;
            font-weight: 600;
        }}
        .file-tree {{
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
            background: var(--bg-secondary);
            border-radius: 6px;
            border: 1px solid var(--border-color);
            margin: 15px 0;
        }}
        .tree-item {{
            padding: 6px 0;
            border-bottom: 1px solid var(--border-color);
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
        }}
        .tree-item:last-child {{
            border-bottom: none;
        }}
        .tree-item code {{
            color: var(--text-primary);
            background: transparent;
            border: none;
            padding: 0;
        }}
        .tree-line {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            white-space: pre;
            color: var(--text-primary);
            margin: 0;
            padding: 0;
        }}
        .tree-connector {{
            color: var(--text-secondary);
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        .tree-dir {{
            color: var(--accent-color);
            font-weight: 600;
        }}
        .tree-file {{
            color: var(--text-primary);
        }}
        .copy-btn, .copy-btn-small {{
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
            margin: 5px;
        }}
        .copy-btn-small {{
            padding: 4px 8px;
            font-size: 11px;
        }}
        .copy-btn:hover, .copy-btn-small:hover {{
            background: var(--accent-color);
            opacity: 0.8;
            transform: scale(1.05);
        }}
        .copy-container {{
            margin-bottom: 10px;
            text-align: right;
        }}
        .copyable {{
            cursor: pointer;
            position: relative;
        }}
        .copyable:hover {{
            background: rgba(88, 166, 255, 0.1);
        }}
    </style>
    <script>
        // Theme toggle
        function toggleTheme() {{
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('r2s-theme', newTheme);
        }}
        
        // Load saved theme
        (function() {{
            const savedTheme = localStorage.getItem('r2s-theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
        }})();
        
        // Copy to clipboard function
        function copyToClipboard(text) {{
            // If text is an ID, get the element's content
            const element = document.getElementById(text);
            let textToCopy = text;
            
            if (element) {{
                if (element.tagName === 'TABLE') {{
                    // Copy table as CSV
                    const rows = element.querySelectorAll('tbody tr');
                    let csv = '';
                    rows.forEach(row => {{
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 2) {{
                            csv += cells[0].textContent.trim() + '=' + cells[1].textContent.trim() + '\\n';
                        }}
                    }});
                    textToCopy = csv;
                }} else if (element.tagName === 'PRE' || element.id === 'file-tree-text') {{
                    // For pre elements or file-tree-text, get text content with line breaks
                    textToCopy = element.textContent || element.innerText;
                }} else {{
                    textToCopy = element.textContent || element.innerText;
                }}
            }}
            
            // Create temporary textarea
            const textarea = document.createElement('textarea');
            textarea.value = textToCopy;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            
            try {{
                document.execCommand('copy');
                // Show feedback
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                btn.style.background = 'var(--success-color)';
                setTimeout(() => {{
                    btn.textContent = originalText;
                    btn.style.background = 'var(--accent-color)';
                }}, 2000);
            }} catch (err) {{
                console.error('Failed to copy:', err);
                alert('Failed to copy to clipboard');
            }}
            
            document.body.removeChild(textarea);
        }}
        
        // Add click handlers to copyable elements
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.copyable').forEach(el => {{
                el.addEventListener('click', function() {{
                    const value = this.getAttribute('data-value') || this.textContent;
                    copyToClipboard(value);
                }});
            }});
        }});
    </script>
</head>
<body>
<button class="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark mode">
    🌓 Theme
</button>
<div class="container">
{formatter.format_html_header(self.start_time, end_time, len(self.results))}
"""
            
            # Use formatter to generate content
            html += formatter.format_html_content(self.results)
            
            # Add quick copy section for important results
            html += self._generate_quick_copy_section()
            
            html += """
</div>
</body>
</html>
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<html><body><h1>Error generating report: {e}</h1></body></html>")
    
    def export_csv(self, filename: str):
        """Export results to CSV file - only for simple operations without complex data."""
        no_csv_operations = ['secrets', 'system_info', 'code', 'module', 'read_file']
        
        if self.operation_type in no_csv_operations:
            return
        
        if not self.results:
            return
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            fieldnames = ['timestamp', 'type', 'status', 'command', 'output', 'error']
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for result in self.results:
                    if result.get('data') or result.get('type') in ['secrets', 'system_info', 'code', 'module']:
                        continue
                    
                    row = {
                        'timestamp': result.get('timestamp', ''),
                        'type': result.get('type', 'command'),
                        'status': 'SUCCESS' if result.get('success') else 'FAILED',
                        'command': str(result.get('command', ''))[:500] if result.get('command') else '',
                        'output': str(result.get('output', ''))[:1000] if result.get('output') else '',
                        'error': str(result.get('error', ''))[:500] if result.get('error') else ''
                    }
                    
                    try:
                        writer.writerow(row)
                    except Exception:
                        continue
        except Exception:
            pass
    
    def export_txt(self, filename: str):
        """Export results to plain text file with operation-specific formatting."""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        try:
            formatter = get_formatter(self.operation_type)
            end_time = datetime.now()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatter.format_txt_header(self.start_time, end_time, len(self.results)))
                f.write(formatter.format_txt_content(self.results))
        except Exception as e:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Error generating report: {e}\n")
                f.write(f"Operation: {self.operation_type}\n")
                f.write(f"Total Results: {len(self.results)}\n")

