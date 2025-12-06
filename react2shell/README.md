# React2Shell - Modular Architecture

This document describes the modular architecture of React2Shell (R2S), the core package for the R2S security testing tool.

## 📁 Structure

```
react2shell/
├── main.py              # Main entry point and argument parsing
├── classes/             # Core classes
│   ├── detector.py     # Target detection and information gathering
│   ├── executor.py     # Command execution and payload sending
│   ├── modules.py      # Exploit modules system (Metasploit-style)
│   ├── operations.py   # High-level exploitation operations
│   ├── payload.py      # Payload building, randomization, and warming
│   └── shell.py        # Interactive shell with history and navigation
├── services/            # Services
│   ├── config.py       # Configuration management (JSON format)
│   ├── exporter.py     # File and archive export functionality
│   ├── formatters.py   # Operation-specific report formatters
│   ├── history.py      # Command history persistence
│   ├── logger.py       # Logging and audit trails
│   ├── proxy.py        # Proxy management and rotation
│   └── reporter.py     # Report generation (JSON/HTML/TXT/CSV)
└── utils/              # Utilities
    ├── colors.py       # ANSI color codes and colorization
    └── helpers.py      # Helper functions (path handling, result extraction)
```

## 🏗️ Architecture Overview

### Main Entry Point (`main.py`)

- Handles command-line argument parsing
- Orchestrates all modules and services
- Manages configuration loading and saving
- Coordinates operations (test, shell, export, modules, etc.)
- Handles special commands (settings, cleanup, uninstall)

### Classes (`classes/`)

**`detector.py`** - Target Detection
- Detects target platform (Unix/Linux, Windows)
- Identifies server type (Next.js, etc.)
- Gathers initial system information

**`executor.py`** - Command Execution
- Sends payloads via multipart form data
- Handles HTTP redirects (301, 302, 303, 307, 308)
- Extracts command output from responses
- Implements WAF bypass techniques
- Supports parallel execution
- Handles Next.js 404 page detection

**`modules.py`** - Exploit Modules System
- Base `ExploitModule` class for extensibility
- Built-in modules:
  - `EnvDumpModule` - Dump environment variables
  - `FileSearchModule` - Search for files by pattern
  - `NetworkScanModule` - Network scanning
  - `ProcessListModule` - List running processes
- Module registry system
- Module option handling

**`operations.py`** - High-Level Operations
- `test_vulnerability()` - Test for CVE-2025-55182
- `list_directory()` - List directory contents
- `read_file()` - Read file contents
- `get_system_info()` - Gather system information
- `get_app_secrets()` - Attempt to read secrets
- `get_app_code()` - Attempt to read source code
- `custom_command()` - Execute custom commands

**`payload.py`** - Payload Management
- `PayloadBuilder` - Build RCE payloads
- `PayloadRandomizer` - Randomize payloads to evade detection
- `PayloadWarmer` - Auto-warm and optimize payloads

**`shell.py`** - Interactive Shell
- Full interactive shell session over HTTPS
- Command history with arrow key navigation (↑/↓)
- Cursor movement (←/→)
- Command aliases (nano/vi/vim/emacs → cat, clear → cls)
- Colored file/folder output in `ls`
- Persistent history saved to `~/.r2s/history`
- Auto-save shell session reports
- Special command handling (cd, exit, quit)

### Services (`services/`)

**`config.py`** - Configuration Management
- JSON-based configuration stored at `~/.r2s/config.json`
- Interactive settings panel (`r2s settings`)
- Self-healing (handles corrupted files)
- Default configuration with sensible defaults
- Per-operation report format configuration

**`exporter.py`** - Export Functionality
- `export_file()` - Export single files
- `export_archive()` - Export entire app directories as zip archives
- Handles binary files (zip, tar.gz) with base64 encoding
- Automatically excludes `.gitignore` patterns
- Reads `.gitignore` from server if available
- Auto-cleanup of server-side archives after download
- Configurable export directory

**`formatters.py`** - Report Formatters
- Operation-specific formatters:
  - `SecretsFormatter` - Format secrets extraction results
  - `SystemInfoFormatter` - Format system information
  - `CodeFormatter` - Format code extraction results
  - `ModuleFormatter` - Format module results
  - `ExportFormatter` - Format export results
  - `GenericFormatter` - Fallback formatter
- HTML, JSON, TXT format support
- Copy buttons and theme toggle for HTML reports

**`history.py`** - Command History
- Persistent command history
- Saved to `~/.r2s/history`
- Integration with `readline` for history navigation

**`logger.py`** - Logging and Audit Trails
- Detailed logging of all operations
- Saved to `~/.r2s/logs/audit.log`
- Timestamped entries
- Operation tracking

**`proxy.py`** - Proxy Management
- HTTP proxy support
- Proxy rotation from file
- Proxy authentication support

**`reporter.py`** - Report Generation
- Auto-save reports to `~/.r2s/reports/`
- Human-readable timestamps (YYYYMMDD_HHMMSS)
- Multiple formats: JSON, HTML, TXT, CSV
- Operation-specific formatting
- ANSI color code stripping for reports
- HTML reports with dark/light mode
- Copy buttons for easy data extraction

### Utilities (`utils/`)

**`colors.py`** - Color Utilities
- ANSI color codes
- `colorize()` function for colored output
- `disable_colors()` for no-color mode

**`helpers.py`** - Helper Functions
- `get_r2s_home()` - Get `~/.r2s/` directory
- `extract_result_from_redirect()` - Extract results from redirect headers
- `strip_ansi_codes()` - Remove ANSI codes from text
- `print_banner()` - Print tool banner
- `print_section_header()` - Print section headers

## 🔄 Data Flow

1. **User Input** → `main.py` (argument parsing)
2. **Configuration** → `config.py` (load settings)
3. **Target Detection** → `detector.py` (gather info)
4. **Operation Execution** → `operations.py` or `shell.py` or `modules.py`
5. **Command Execution** → `executor.py` (send payloads)
6. **Payload Building** → `payload.py` (if needed)
7. **Result Processing** → `reporter.py` (save reports)
8. **Logging** → `logger.py` (audit trail)

## 📊 Report Generation Flow

1. **Operation** → Sets operation type in `Reporter`
2. **Data Collection** → `reporter.add_operation_data()` or `reporter.add_shell_command()`
3. **Formatting** → `formatters.py` (operation-specific formatting)
4. **Export** → `reporter.export_json/html/txt/csv()`
5. **Auto-Save** → Saved to `~/.r2s/reports/` with timestamp

## 🔧 Configuration System

Configuration is stored in JSON format at `~/.r2s/config.json`:

```json
{
  "report": {
    "auto_save": true,
    "default_format": ["html", "json", "txt"],
    "shell_formats": ["html", "json", "txt"],
    "test_formats": ["html", "json", "txt"],
    "reports_dir": "~/.r2s/reports"
  },
  "export": {
    "export_dir": "~/.r2s/exports"
  },
  "shell": {
    "history_file": "~/.r2s/history"
  },
  "execution": {
    "default_timeout": 10
  }
}
```

## 🎯 Key Features

- ✅ Modular architecture with clear separation of concerns
- ✅ Interactive shell with arrow key navigation
- ✅ Command history persistence
- ✅ Logging and audit trails
- ✅ Report generation (JSON/HTML/TXT) with operation-specific formatters
- ✅ Configuration file support (JSON format)
- ✅ File and archive export functionality
- ✅ Exploit modules system (Metasploit-style)
- ✅ Proxy support with rotation
- ✅ Auto-save reports with configurable formats
- ✅ ANSI color code stripping for reports
- ✅ HTML reports with dark/light mode and copy buttons

## 📝 Usage

```bash
# Run as Python module
python3 -m react2shell.main -u https://target.com -t

# Or use the built binary
r2s -u https://target.com -t
```

## 🔗 Related Documentation

- **Main README:** See [`../README.md`](../README.md) for full tool documentation
- **Testing Environment:** See [`../nextjs/README.md`](../nextjs/README.md) for testing setup

---

## 👨‍💻 Developer

**zamdevio**

- GitHub: [https://github.com/zamdevio](https://github.com/zamdevio)
- Project Repository: [https://github.com/zamdevio/r2s](https://github.com/zamdevio/r2s)

---

<div align="center">

**Part of the R2S (React2Shell) Security Testing Tool**

[⬆ Back to Main README](../README.md)

</div>
