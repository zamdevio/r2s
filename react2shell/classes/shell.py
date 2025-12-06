"""Interactive shell with arrow key support for React2Shell."""

import os
import re
from typing import Optional, List
from urllib.parse import unquote

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

from ..classes.executor import execute_command
from ..utils.colors import Colors, colorize
from ..utils.helpers import print_section_header


class InteractiveShell:
    """Interactive shell session over HTTPS with arrow key support."""
    
    def __init__(self, target_url: str, timeout: int = 10, verify_ssl: bool = True, 
                 windows: bool = False, history_file: Optional[str] = None, 
                 follow_redirects: bool = True, reporter=None, config=None):
        self.target_url = target_url
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.windows = windows
        self.running = False
        self.pwd = "/"
        self.follow_redirects = follow_redirects
        self.last_history_command = None
        self.history_index = -1
        self.reporter = reporter
        self.command_history = []
        self.last_exec_result = None
        self.config = config
        
        if READLINE_AVAILABLE:
            if history_file:
                readline.set_history_length(1000)
                try:
                    readline.read_history_file(history_file)
                    self._clean_history_duplicates()
                except FileNotFoundError:
                    pass
                self.history_file = history_file
            else:
                home = os.path.expanduser("~")
                from ..utils.helpers import get_r2s_home
                r2s_home = get_r2s_home()
                self.history_file = str(r2s_home / "history")
                try:
                    readline.read_history_file(self.history_file)
                    self._clean_history_duplicates()
                except FileNotFoundError:
                    pass
                readline.set_history_length(1000)
        else:
            self.history_file = None
            try:
                from react2shell.services.history import CommandHistory
                self.history = CommandHistory(history_file=history_file)
            except ImportError:
                self.history = None
    
    def format_ls_output(self, output: str) -> str:
        """Format ls output with colors - directories in blue with trailing slash, files by extension."""
        if not output or not Colors:
            return output
        
        lines = output.split('\n')
        formatted_lines = []
        items_to_check = []
        
        for line in lines:
            if not line.strip() or line.strip().startswith('total'):
                formatted_lines.append(line)
                continue
            
            parts = line.split()
            if len(parts) == 0:
                formatted_lines.append(line)
                continue
            
            is_dir = False
            item_name = ""
            
            if len(parts) > 8:
                item_name = ' '.join(parts[8:]).rstrip('/')
                if parts[0].startswith('d'):
                    is_dir = True
            elif len(parts) > 0:
                item_name = parts[-1].rstrip('/')
                if parts[-1].endswith('/'):
                    is_dir = True
                    item_name = item_name.rstrip('/')
                else:
                    items_to_check.append((len(formatted_lines), line, item_name, parts))
                    formatted_lines.append(None)
                    continue
            
            if item_name in ['.', '..']:
                formatted_lines.append(line)
                continue
            
            if is_dir:
                if len(parts) > 8:
                    new_parts = parts[:8] + [item_name + '/']
                    line = ' '.join(new_parts)
                else:
                    line = line.rstrip() + '/' if not line.rstrip().endswith('/') else line
                formatted_lines.append(colorize(line, Colors.BLUE + Colors.BOLD))
            else:
                formatted_lines.append(self._colorize_file_line(line, item_name, parts))
        
        if items_to_check and len(items_to_check) > 0:
            item_names = [item[2] for item in items_to_check]
            check_items = ' '.join([f'"{name}"' for name in item_names])
            check_cmd = f'for item in {check_items}; do test -d "$item" && echo "$item:DIR" || echo "$item:FILE"; done'
            
            check_result = execute_command(
                self.target_url,
                f'cd "{self.pwd}" && {check_cmd}',
                self.timeout,
                self.verify_ssl,
                self.windows,
                base64_encode=True,
                follow_redirects=self.follow_redirects
            )
            
            dir_map = {}
            if check_result.get("success"):
                for result_line in check_result.get("output", "").split('\n'):
                    if ':' in result_line:
                        try:
                            name, typ = result_line.split(':', 1)
                            if typ.strip() == 'DIR':
                                dir_map[name.strip()] = True
                        except:
                            pass
            
            for orig_idx, line, item_name, parts in items_to_check:
                is_dir = dir_map.get(item_name, False)
                if is_dir:
                    formatted_line = line.rstrip() + '/' if not line.rstrip().endswith('/') else line
                    formatted_lines[orig_idx] = colorize(formatted_line, Colors.BLUE + Colors.BOLD)
                else:
                    formatted_lines[orig_idx] = self._colorize_file_line(line, item_name, parts)
        
        return '\n'.join([l for l in formatted_lines if l is not None])
    
    def _colorize_file_line(self, line: str, item_name: str, parts: list) -> str:
        """Colorize a file line based on extension and permissions."""
        file_ext = item_name.split('.')[-1].lower() if '.' in item_name else ''
        
        if len(parts) > 0 and parts[0] and len(parts[0]) > 6 and 'x' in parts[0][3:6]:
            return colorize(line, Colors.MAGENTA + Colors.BOLD)
        elif file_ext in ['py', 'js', 'ts', 'tsx', 'jsx', 'sh', 'bash', 'zsh', 'fish']:
            return colorize(line, Colors.CYAN)
        elif file_ext in ['json', 'yaml', 'yml', 'toml', 'xml', 'ini', 'conf', 'config']:
            return colorize(line, Colors.YELLOW)
        elif file_ext in ['md', 'txt', 'log', 'readme', 'license', 'changelog']:
            return colorize(line, Colors.WHITE)
        elif file_ext in ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico']:
            return colorize(line, Colors.GREEN)
        elif file_ext in ['zip', 'tar', 'gz', 'bz2', 'xz', '7z', 'rar']:
            return colorize(line, Colors.MAGENTA)
        else:
            return colorize(line, Colors.YELLOW)
    
    def _filter_arrow_keys(self, text: str) -> str:
        """Filter out arrow key escape sequences."""
        import re
        if not text:
            return text
        
        text = re.sub(r'\x1b\[[ABCD]', '', text)
        text = re.sub(r'\x1bO[ABCD]', '', text)
        text = re.sub(r'\^\[\[[ABCD]', '', text)
        text = re.sub(r'\^\x5b\x5b[ABCD]', '', text)
        text = re.sub(r'\x1b\[[0-9;]*[ABCDHJK]', '', text)
        text = re.sub(r'\x1b\[[0-9;]*[^m]', '', text)
        
        if not text.strip() or text.strip() in ['^[[A', '^[[B', '^[[C', '^[[D']:
            return ''
        
        return text.strip()
    
    def _clean_history_duplicates(self):
        """Remove consecutive duplicate commands from readline history."""
        if not READLINE_AVAILABLE:
            return
        
        try:
            history_len = readline.get_current_history_length()
            if history_len <= 1:
                return
            
            # Get all history items
            history_items = []
            for i in range(1, history_len + 1):
                try:
                    item = readline.get_history_item(i)
                    history_items.append(item)
                except (IndexError, ValueError):
                    break
            
            # Clear history
            readline.clear_history()
            
            # Re-add without consecutive duplicates
            last_item = None
            for item in history_items:
                if item != last_item:
                    readline.add_history(item)
                    last_item = item
        except Exception:
            # If cleaning fails, just continue with existing history
            pass
    
    def get_input_with_arrows(self, prompt: str) -> str:
        """Get input with arrow key support and duplicate-skipping history."""
        if READLINE_AVAILABLE:
            # Reset history index for new input
            self._dedup_history_index = None
            
            # Configure readline - use default history search but we'll filter when adding
            try:
                readline.parse_and_bind(r'"\e[A": history-search-backward')
                readline.parse_and_bind(r'"\e[B": history-search-forward')
                readline.parse_and_bind(r'"\e[C": forward-char')
                readline.parse_and_bind(r'"\e[D": backward-char')
                readline.parse_and_bind(r'"\eOA": history-search-backward')
                readline.parse_and_bind(r'"\eOB": history-search-forward')
                readline.parse_and_bind(r'"\eOC": forward-char')
                readline.parse_and_bind(r'"\eOD": backward-char')
            except:
                pass
            
            try:
                user_input = input(prompt)
                return self._filter_arrow_keys(user_input)
            except (EOFError, KeyboardInterrupt):
                raise
        else:
            try:
                user_input = input(prompt)
                return self._filter_arrow_keys(user_input)
            except (EOFError, KeyboardInterrupt):
                raise
    
    def execute(self, command: str) -> Optional[str]:
        """Execute a command and return output."""
        command = self._filter_arrow_keys(command)
        
        if not command.strip():
            return None
        
        # Handle shell built-ins
        if command.strip() == "exit" or command.strip() == "quit":
            self.running = False
            return None
        
        if command.strip() == "clear":
            import os
            os.system('clear' if os.name != 'nt' else 'cls')
            return None
        
        # Handle cd command (same as before)
        if command.strip() == "cd" or command.strip().startswith("cd "):
            if command.strip() == "cd":
                new_dir = "~"
            else:
                new_dir = command.strip()[3:].strip().strip('"\'')
                if not new_dir or new_dir == "~":
                    new_dir = "~"
            
            if new_dir == "~" or new_dir.startswith("~/"):
                if self.windows:
                    cd_cmd = 'cd %USERPROFILE% && cd'
                else:
                    cd_cmd = 'cd ~ && pwd'
            elif new_dir == "..":
                if self.windows:
                    cd_cmd = 'cd .. && cd'
                else:
                    cd_cmd = 'cd .. && pwd'
            else:
                if self.windows:
                    cd_cmd = f'cd /d "{new_dir}" && cd'
                else:
                    cd_cmd = f'cd "{new_dir}" && pwd'
            
            result = execute_command(
                self.target_url, cd_cmd, self.timeout, self.verify_ssl,
                self.windows, base64_encode=True, follow_redirects=self.follow_redirects
            )
            
            if result.get("success") and result.get("output"):
                output = result.get("output", "").strip()
                output = output.replace("Vulnerable (redirect detected:", "").strip()
                output = output.split('\n')[0].strip()
                if output:
                    self.pwd = output
                    return None
            return colorize(f"cd: {new_dir}: No such file or directory", Colors.RED) if Colors else f"cd: {new_dir}: No such file or directory"
        
        cmd_parts = command.strip().split()
        if cmd_parts:
            cmd = cmd_parts[0].lower()
            if cmd in ['nano', 'vi', 'vim', 'emacs']:
                if len(cmd_parts) > 1:
                    command = f'cat "{cmd_parts[1]}"'
                else:
                    return colorize("Error: No file specified. Use: cat <file>", Colors.RED) if Colors else "Error: No file specified"
            elif cmd == 'sudo' and len(cmd_parts) > 1:
                command = ' '.join(cmd_parts[1:])
        
        # Build full command
        if self.pwd != "/" and self.pwd and not self.windows:
            safe_pwd = self.pwd.replace('"', '\\"')
            full_cmd = f'cd "{safe_pwd}" && {command}'
        else:
            full_cmd = command
        
        exec_result = execute_command(
            self.target_url, full_cmd, self.timeout, self.verify_ssl,
            self.windows, base64_encode=True, follow_redirects=self.follow_redirects
        )
        
        self.last_exec_result = exec_result
        
        if exec_result.get("success") and not exec_result.get("is_404", False):
            output = exec_result.get("output", "")
            raw_response = exec_result.get("raw_response", "")
            
            if "Vulnerable (redirect detected:" in output:
                error_msg = None
                
                if raw_response and "_not-found" in raw_response:
                    error_msg = "Command not found (404)"
                elif raw_response:
                    nextjs_match = re.search(r'"message"\s*:\s*"([^"]+)"', raw_response, re.IGNORECASE)
                    if nextjs_match:
                        error_msg = nextjs_match.group(1)
                    else:
                        shell_error = re.search(r'(/bin/sh:\s*\d+:\s*[^:]+:\s*[^\n"]+)', raw_response, re.IGNORECASE)
                        if shell_error:
                            error_msg = shell_error.group(1)
                
                if error_msg:
                    return colorize(f"Error: {error_msg}", Colors.RED) if Colors else f"Error: {error_msg}"
                else:
                    return colorize("Command executed but output not captured.", Colors.YELLOW) if Colors else "Command executed but output not captured."
            # Format ls output (all variants: ls, ls -la, ls -l, etc.)
            cmd_lower = command.strip().lower()
            if cmd_lower.startswith('ls ') or cmd_lower == 'ls':
                output = self.format_ls_output(output)
            return output
        elif exec_result.get("is_404", False):
            # Next.js 404 detected - command or file not found
            error_msg = exec_result.get("error", "Command or file not found")
            return colorize(f"Error: {error_msg}", Colors.RED) if Colors else f"Error: {error_msg}"
        else:
            error = exec_result.get('error', 'Unknown error')
            if exec_result.get("vulnerable") and exec_result.get("status_code") in [301, 302, 303, 307]:
                return colorize("Command executed (redirect detected). Output may not be captured.", Colors.YELLOW) if Colors else "Command executed (redirect detected)."
            return colorize(f"Error: {error}", Colors.RED) if Colors else f"Error: {error}"
    
    def start(self):
        """Start interactive shell session."""
        self.running = True
        print_section_header("INTERACTIVE SHELL")
        print(colorize("[*] Starting interactive shell session...", Colors.CYAN) if Colors else "[*] Starting shell...")
        print(colorize("[*] Type 'exit' or 'quit' to exit", Colors.CYAN) if Colors else "[*] Type 'exit' to exit")
        print(colorize("[*] Arrow keys: ↑/↓ for history, ←/→ for cursor", Colors.CYAN) if Colors else "[*] Use arrow keys for history")
        
        # Compact command aliases info
        aliases_info = colorize("Commands: ", Colors.CYAN) if Colors else "Commands: "
        aliases_info += "nano/vi/vim/emacs→cat, sudo→auto-removed, clear→cls"
        print(aliases_info)
        print()
        
        # Get initial directory
        if not self.windows:
            pwd_result = execute_command(
                self.target_url, "pwd", self.timeout, self.verify_ssl,
                self.windows, base64_encode=True, follow_redirects=self.follow_redirects
            )
            if pwd_result.get("success") and pwd_result.get("output"):
                self.pwd = pwd_result.get("output", "/").strip()
                self.pwd = self.pwd.replace("Vulnerable (redirect detected:", "").strip()
                self.pwd = self.pwd.split('\n')[0].strip()
            else:
                self.pwd = "/app"
        
        try:
            while self.running:
                display_pwd = self.pwd if self.pwd else "/"
                if len(display_pwd) > 40:
                    display_pwd = "..." + display_pwd[-37:]
                
                if self.windows:
                    prompt = f"r2s@{self.target_url}> "
                else:
                    prompt = f"r2s@{self.target_url}:{display_pwd}$ "
                
                try:
                    command = self.get_input_with_arrows(colorize(prompt, Colors.GREEN + Colors.BOLD) if Colors else prompt)
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                
                # Filter arrow keys again (safety check)
                command = self._filter_arrow_keys(command)
                
                # Skip if command is empty or only escape sequences
                if not command or not command.strip():
                    continue
                
                # Skip if command is just arrow key sequences
                if command.strip() in ['^[[A', '^[[B', '^[[C', '^[[D', '\x1b[A', '\x1b[B', '\x1b[C', '\x1b[D']:
                    continue
                
                # Save to history (skip if same as last command to avoid duplicates)
                if READLINE_AVAILABLE:
                    # Only add if different from last command (prevents consecutive duplicates)
                    last_cmd = None
                    try:
                        history_len = readline.get_current_history_length()
                        if history_len > 0:
                            last_cmd = readline.get_history_item(history_len)
                    except:
                        pass
                    
                    # Only add to history if it's different from the last command
                    if command != last_cmd:
                        readline.add_history(command)
                        if self.history_file:
                            try:
                                readline.write_history_file(self.history_file)
                            except Exception:
                                pass
                elif hasattr(self, 'history') and self.history:
                    if not hasattr(self.history, 'last') or command != getattr(self.history, 'last', None):
                        self.history.add(command)
                        self.history.last = command
                
                output = self.execute(command)
                
                if self.reporter and command.strip() not in ['exit', 'quit', 'clear', 'cd']:
                    if hasattr(self, 'last_exec_result') and self.last_exec_result:
                        success = self.last_exec_result.get("success", False)
                        error = self.last_exec_result.get("error") if not success else None
                    else:
                        success = output is not None and not (isinstance(output, str) and (output.startswith("Error:") or "not captured" in output))
                        error = output if not success and isinstance(output, str) and output.startswith("Error:") else None
                    self.reporter.add_shell_command(command, str(output) if output else "", success, error)
                
                if output is not None:
                    print(output)
                elif not self.running:
                    break
                
        except KeyboardInterrupt:
            print()
            print(colorize("[*] Exiting shell...", Colors.YELLOW) if Colors else "[*] Exiting shell...")
        finally:
            self.running = False
            if READLINE_AVAILABLE and self.history_file:
                try:
                    readline.write_history_file(self.history_file)
                except Exception:
                    pass
            print(colorize("[*] Shell session ended", Colors.CYAN) if Colors else "[*] Shell session ended")
            
            if self.reporter and self.reporter.results:
                self._save_report()
    
    def _save_report(self, formats: Optional[List[str]] = None):
        """Save shell session report."""
        from pathlib import Path
        from datetime import datetime
        
        if formats is None:
            if self.config:
                formats = self.config.get("report", "shell_formats", ["json", "txt", "csv", "html"])
            else:
                formats = ["json", "txt", "csv", "html"]
        
        from ..utils.helpers import get_r2s_home
        reports_dir_str = self.config.get("report", "reports_dir", "~/.r2s/reports") if self.config else "~/.r2s/reports"
        if reports_dir_str.startswith("~"):
            r2s_home = get_r2s_home()
            reports_dir = Path(r2s_home / "reports")
        else:
            reports_dir = Path(reports_dir_str)
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"shell_{timestamp}"
        
        if self.reporter:
            self.reporter.set_operation("shell")
            
            if "json" in formats:
                self.reporter.export_json(reports_dir / f"{base_name}.json")
            if "txt" in formats:
                self.reporter.export_txt(reports_dir / f"{base_name}.txt")
            if "csv" in formats:
                self.reporter.export_csv(reports_dir / f"{base_name}.csv")
            if "html" in formats:
                self.reporter.export_html(reports_dir / f"{base_name}.html")
            
            saved_formats = ", ".join(formats)
            print(colorize(f"[+] Report saved to {reports_dir}/{base_name}.{{{saved_formats}}}", Colors.GREEN) if Colors else f"[+] Report saved to {reports_dir}/{base_name}.*")

