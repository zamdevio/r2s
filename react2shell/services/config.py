"""Configuration service for React2Shell with JSON support."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigError(Exception):
    """Configuration error."""
    pass


class Config:
    """Configuration manager for React2Shell with JSON support."""
    
    DEFAULT_CONFIG = {
        "report": {
            "auto_save": True,
            "default_format": "json",
            "shell_formats": ["json", "txt", "html"],
            "test_formats": ["json", "html", "txt"],
            "command_formats": ["json", "txt", "html"],
            "scan_formats": ["json", "html", "txt"],
            "secrets_formats": ["json", "html", "txt"],
            "system_info_formats": ["json", "html", "txt"],
            "code_formats": ["json", "html", "txt"],
            "list_directory_formats": ["json", "html", "txt"],
            "read_file_formats": ["json", "html", "txt"],
            "custom_command_formats": ["json", "html", "txt"],
            "module_formats": ["json", "html", "txt"],
            "export_formats": ["json", "html", "txt"],
            "reports_dir": "~/.r2s/reports"
        },
        "shell": {
            "history_file": "~/.r2s/history",
            "history_length": 1000,
            "follow_redirects": True,
            "timeout": 10
        },
        "execution": {
            "timeout": 10,
            "follow_redirects": True,
            "waf_bypass": False,
            "auto_warm": False,
            "randomize": False,
            "base64_encode": True
        },
        "output": {
            "colors": True,
            "verbose": False
        },
        "export": {
            "export_dir": "~/.r2s/exports"
        },
        "preferences": {
            "timeout": 10,
            "format": None,
            "waf_bypass": False,
            "waf_bypass_size": 128,
            "vercel_waf_bypass": False,
            "header_strategy": "default",
            "auto_warm": False,
            "randomize": False,
            "follow_redirects": True,
            "insecure": False,
            "windows": False,
            "no_color": False,
            "verbose": False,
            "parallel": None,
            "proxy": None,
            "rate": None,
            "delay": None
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        from ..utils.helpers import get_r2s_home
        if config_file is None:
            r2s_home = get_r2s_home()
            self.config_file = r2s_home / "config.json"
        
        self.settings: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.settings = json.load(f)
                self._merge_defaults()
            except Exception as e:
                # If config file is corrupted, reset to defaults silently
                try:
                    self.config_file.unlink()
                except:
                    pass
                self.settings = self.DEFAULT_CONFIG.copy()
                try:
                    self.save()
                except:
                    pass
                # Don't raise error, just use defaults
        else:
            self.settings = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def _merge_defaults(self):
        """Merge loaded config with defaults to ensure all keys exist."""
        for section, defaults in self.DEFAULT_CONFIG.items():
            if section not in self.settings:
                self.settings[section] = defaults.copy()
            else:
                for key, value in defaults.items():
                    if key not in self.settings[section]:
                        self.settings[section][key] = value
    
    def save(self):
        """Save configuration to JSON file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.settings.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value."""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire section."""
        return self.settings.get(section, {}).copy()
    
    def set_section(self, section: str, values: Dict[str, Any]):
        """Set entire section."""
        self.settings[section] = values.copy()
        self.save()
    
    def list_sections(self) -> List[str]:
        """List all configuration sections."""
        return list(self.settings.keys())
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self.settings.copy()


def show_settings_interactive(config: Config):
    """Interactive settings editor - focuses on preferences for settings that apply to all future runs."""
    from ..utils.colors import Colors, colorize
    
    print(colorize("\n╔═══════════════════════════════════════════════════════════╗", Colors.CYAN))
    print(colorize("║         React2Shell Settings Manager                      ║", Colors.CYAN))
    print(colorize("╚═══════════════════════════════════════════════════════════╝\n", Colors.CYAN))
    
    print(colorize("[*] This panel manages settings saved to ~/.r2s/config.json", Colors.YELLOW))
    print(colorize("[*] Command-line arguments (--timeout, etc.) only affect current run", Colors.CYAN))
    print(colorize("[*] Use this panel to set defaults that apply to all future runs\n", Colors.CYAN))
    
    while True:
        sections = config.list_sections()
        print(colorize("Available sections:", Colors.CYAN))
        for i, section in enumerate(sections, 1):
            # Highlight preferences section
            marker = " ⭐ (Recommended)" if section == "preferences" else ""
            print(f"  {i}. {section}{marker}")
        print(f"  {len(sections) + 1}. Exit")
        
        try:
            choice = input(colorize("\nSelect section to edit (number): ", Colors.GREEN))
            if not choice.strip():
                continue
            
            choice_num = int(choice)
            if choice_num == len(sections) + 1:
                print(colorize("\n[+] Settings saved!", Colors.GREEN))
                break
            elif 1 <= choice_num <= len(sections):
                section = sections[choice_num - 1]
                edit_section(config, section)
            else:
                print(colorize("Invalid choice", Colors.RED))
        except (ValueError, KeyboardInterrupt):
            print(colorize("\n[!] Exiting settings panel", Colors.YELLOW))
            break
        except Exception as e:
            print(colorize(f"Error: {e}", Colors.RED))


def edit_section(config: Config, section: str):
    """Edit a configuration section."""
    from ..utils.colors import Colors, colorize
    
    section_data = config.get_section(section)
    
    # Special handling for preferences section
    if section == "preferences":
        print(colorize("\n[*] Preferences Section - These are your default settings", Colors.CYAN))
        print(colorize("[*] These values will be used as defaults for all future runs", Colors.YELLOW))
        print(colorize("[*] You can override them with command-line arguments (--timeout, etc.)\n", Colors.CYAN))
    
    while True:
        print(colorize(f"\n╔═══════════════════════════════════════════════════════════╗", Colors.CYAN))
        print(colorize(f"║              Editing Section: {section:20s}        ║", Colors.CYAN))
        print(colorize("╚═══════════════════════════════════════════════════════════╝\n", Colors.CYAN))
        
        keys = list(section_data.keys())
        print(colorize("Settings:", Colors.CYAN))
        for i, key in enumerate(keys, 1):
            value = section_data[key]
            # Format display value
            if isinstance(value, list):
                display_value = f"[{', '.join(map(str, value))}]"
            elif isinstance(value, bool):
                display_value = "True" if value else "False"
            elif value is None:
                display_value = "None"
            else:
                display_value = str(value)
            print(f"  {i}. {key:25s} = {display_value}")
        print(f"  {len(keys) + 1}. Back")
        
        try:
            choice = input(colorize("\nSelect setting to edit (number): ", Colors.GREEN))
            if not choice.strip():
                continue
            
            choice_num = int(choice)
            if choice_num == len(keys) + 1:
                break
            elif 1 <= choice_num <= len(keys):
                key = keys[choice_num - 1]
                current_value = section_data[key]
                
                # Show helpful hints
                hints = {}
                if section == "preferences":
                    hints = {
                        "timeout": "Request timeout in seconds (0 = no timeout)",
                        "format": "Default report format: json, html, or txt",
                        "waf_bypass": "Enable WAF bypass by default (true/false)",
                        "waf_bypass_size": "WAF bypass size in KB (default: 128)",
                        "header_strategy": "Header strategy: default, chrome_latest, firefox, minimal, assetnote",
                        "auto_warm": "Auto-warm payloads by default (true/false)",
                        "randomize": "Randomize payloads by default (true/false)",
                        "follow_redirects": "Follow redirects by default (true/false)",
                        "insecure": "Disable SSL verification by default (true/false)",
                        "windows": "Use Windows commands by default (true/false)",
                        "no_color": "Disable colors by default (true/false)",
                        "verbose": "Verbose output by default (true/false)",
                    }
                elif section == "export":
                    hints = {
                        "export_dir": "Directory for exported files (default: ~/.r2s/exports). Files are saved as {export_dir}/{domain}/{file_path}",
                    }
                
                if key in hints:
                    print(colorize(f"[*] Hint: {hints[key]}", Colors.CYAN))
                
                new_value = input(colorize(f"Enter new value for {key} (current: {current_value}, empty to go back): ", Colors.GREEN))
                
                if not new_value.strip():
                    # Empty value = go back
                    print(colorize("[*] Going back...", Colors.YELLOW))
                    break
                
                try:
                    if isinstance(current_value, bool):
                        new_value = new_value.strip().lower() in ('true', '1', 'yes', 'on', 'y')
                    elif isinstance(current_value, int):
                        new_value = int(new_value.strip())
                    elif isinstance(current_value, float):
                        new_value = float(new_value.strip())
                    elif isinstance(current_value, list):
                        # For lists, expect comma-separated values
                        new_value = [v.strip() for v in new_value.split(',') if v.strip()]
                    elif current_value is None:
                        # Try to infer type
                        new_value_stripped = new_value.strip()
                        if new_value_stripped.lower() in ('true', 'false', '1', '0', 'yes', 'no'):
                            new_value = new_value_stripped.lower() in ('true', '1', 'yes')
                        elif new_value_stripped.isdigit():
                            new_value = int(new_value_stripped)
                        elif '.' in new_value_stripped and new_value_stripped.replace('.', '').isdigit():
                            new_value = float(new_value_stripped)
                        else:
                            # Keep as string
                            new_value = new_value_stripped
                    else:
                        # Keep as string
                        new_value = new_value.strip()
                    
                    config.set(section, key, new_value)
                    section_data[key] = new_value
                    print(colorize(f"[+] Updated {section}.{key} = {new_value}", Colors.GREEN))
                    if section == "preferences":
                        print(colorize("[*] This setting will apply to all future runs", Colors.CYAN))
                except ValueError:
                    print(colorize(f"[-] Invalid value type for {key}", Colors.RED))
            else:
                print(colorize("Invalid choice", Colors.RED))
        except (ValueError, KeyboardInterrupt):
            break
        except Exception as e:
            print(colorize(f"Error: {e}", Colors.RED))
