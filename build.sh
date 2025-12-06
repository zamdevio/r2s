#!/bin/bash
# Build script for r2s - React2Shell CVE-2025-55182 Exploitation Tool
# Creates a standalone binary using PyInstaller

set -e

# Color codes
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
MAGENTA='\033[95m'
CYAN='\033[96m'
WHITE='\033[97m'
BOLD='\033[1m'
RESET='\033[0m'
BROWN='\033[38;5;130m'
COFFEE='\033[38;5;94m'

# Color functions
colorize() {
    local color=$1
    shift
    echo -e "${color}${*}${RESET}"
}

# Detect environment type
detect_environment() {
    # Check for Termux
    if [ -n "$PREFIX" ] && [[ "$PREFIX" == *"com.termux"* ]]; then
        echo "termux"
        return
    fi
    
    # Check for Android (Termux alternative detection)
    if [ -f "/system/build.prop" ] || [ -d "/data/data/com.termux" ]; then
        echo "termux"
        return
    fi
    
    # Check for Linux distributions
    if [ -f "/etc/os-release" ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|linuxmint|pop|elementary)
                echo "ubuntu"
                ;;
            arch|manjaro|endeavouros)
                echo "arch"
                ;;
            fedora|rhel|centos|rocky|almalinux)
                echo "fedora"
                ;;
            opensuse*|sles)
                echo "opensuse"
                ;;
            alpine)
                echo "alpine"
                ;;
            gentoo)
                echo "gentoo"
                ;;
            *)
                echo "linux"
                ;;
        esac
        return
    fi
    
    # Check for macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
        return
    fi
    
    # Default to generic Linux
    echo "linux"
}

# Get installation paths based on environment
get_install_paths() {
    local env=$1
    
    case "$env" in
        termux)
            # Termux: use $PREFIX/bin (no sudo needed)
            INSTALL_DIR="$PREFIX/bin"
            INSTALL_CMD="cp"
            NEEDS_SUDO=false
            ;;
        ubuntu|arch|fedora|opensuse|alpine|gentoo|linux)
            # Standard Linux: use /usr/local/bin (requires sudo)
            INSTALL_DIR="/usr/local/bin"
            INSTALL_CMD="sudo cp"
            NEEDS_SUDO=true
            ;;
        macos)
            # macOS: use /usr/local/bin (may require sudo)
            INSTALL_DIR="/usr/local/bin"
            INSTALL_CMD="sudo cp"
            NEEDS_SUDO=true
            ;;
        *)
            # Default: use /usr/local/bin
            INSTALL_DIR="/usr/local/bin"
            INSTALL_CMD="sudo cp"
            NEEDS_SUDO=true
            ;;
    esac
}

# Install binary to system
install_binary() {
    local env=$1
    local binary_path=$2
    
    get_install_paths "$env"
    
    echo ""
    if [ "$NEEDS_SUDO" = true ]; then
        echo -ne "${YELLOW}[?] Install to $INSTALL_DIR for global use? (requires sudo) [y/N]: ${RESET}"
    else
        echo -ne "${YELLOW}[?] Install to $INSTALL_DIR for global use? [y/N]: ${RESET}"
    fi
    
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$NEEDS_SUDO" = true ]; then
            # Check if sudo is available
            if ! command -v sudo &> /dev/null; then
                colorize "$RED" "[-] Error: sudo not found. Cannot install to system directory."
                colorize "$CYAN" "[*] You can manually copy the binary:"
                echo -e "    ${CYAN}cp $binary_path $INSTALL_DIR/r2s${RESET}"
                echo -e "    ${CYAN}chmod +x $INSTALL_DIR/r2s${RESET}"
                return
            fi
            
            # Try to install with sudo
            if sudo cp "$binary_path" "$INSTALL_DIR/r2s" 2>/dev/null; then
                sudo chmod +x "$INSTALL_DIR/r2s"
                colorize "$GREEN" "[+] Installed to $INSTALL_DIR/r2s"
                colorize "$CYAN" "[*] You can now run: ${BLUE}r2s --help${RESET}"
            else
                colorize "$RED" "[-] Installation failed. You may need root privileges."
                colorize "$CYAN" "[*] To install manually:"
                echo -e "    ${CYAN}sudo cp $binary_path $INSTALL_DIR/r2s${RESET}"
                echo -e "    ${CYAN}sudo chmod +x $INSTALL_DIR/r2s${RESET}"
            fi
        else
            # No sudo needed (Termux)
            if cp "$binary_path" "$INSTALL_DIR/r2s" 2>/dev/null; then
                chmod +x "$INSTALL_DIR/r2s"
                colorize "$GREEN" "[+] Installed to $INSTALL_DIR/r2s"
                colorize "$CYAN" "[*] You can now run: ${BLUE}r2s --help${RESET}"
            else
                colorize "$RED" "[-] Installation failed. Check permissions."
                colorize "$CYAN" "[*] To install manually:"
                echo -e "    ${CYAN}cp $binary_path $INSTALL_DIR/r2s${RESET}"
                echo -e "    ${CYAN}chmod +x $INSTALL_DIR/r2s${RESET}"
            fi
        fi
    else
        colorize "$CYAN" "[*] To install manually:"
        if [ "$NEEDS_SUDO" = true ]; then
            echo -e "    ${CYAN}sudo cp $binary_path $INSTALL_DIR/r2s${RESET}"
            echo -e "    ${CYAN}sudo chmod +x $INSTALL_DIR/r2s${RESET}"
        else
            echo -e "    ${CYAN}cp $binary_path $INSTALL_DIR/r2s${RESET}"
            echo -e "    ${CYAN}chmod +x $INSTALL_DIR/r2s${RESET}"
        fi
    fi
}

# Check if cleanup command
if [ "$1" == "cleanup" ]; then
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║              Cleaning Build Artifacts                      ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${RESET}"
    
    colorize "$YELLOW" "[*] The following will be removed:"
    echo "    - build/ directory"
    echo "    - dist/ directory"
    echo "    - __pycache__/ directories (recursively)"
    echo "    - *.pyc files"
    echo "    - *.pyo files"
    echo "    - *.spec files (PyInstaller spec files)"
    echo ""
    
    echo -ne "${YELLOW}[?] Continue? [y/N]: ${RESET}"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        colorize "$CYAN" "[-] Cleanup cancelled"
        exit 0
    fi
    
    echo ""
    colorize "$CYAN" "[*] Cleaning build artifacts..."
    
    # Remove build directories
    if [ -d "build" ]; then
        rm -rf build/
        colorize "$GREEN" "[+] Removed build/ directory"
    fi
    
    if [ -d "dist" ]; then
        rm -rf dist/
        colorize "$GREEN" "[+] Removed dist/ directory"
    fi
    
    # Remove PyInstaller spec files
    find . -maxdepth 1 -name "*.spec" -type f -delete 2>/dev/null
    if [ $? -eq 0 ]; then
        colorize "$GREEN" "[+] Removed *.spec files"
    fi
    
    # Remove __pycache__ directories recursively
    PY_CACHE_COUNT=$(find . -type d -name "__pycache__" | wc -l)
    if [ $PY_CACHE_COUNT -gt 0 ]; then
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
        colorize "$GREEN" "[+] Removed $PY_CACHE_COUNT __pycache__ directory(ies)"
    fi
    
    # Remove .pyc files
    PYC_COUNT=$(find . -type f -name "*.pyc" | wc -l)
    if [ $PYC_COUNT -gt 0 ]; then
        find . -type f -name "*.pyc" -delete 2>/dev/null
        colorize "$GREEN" "[+] Removed $PYC_COUNT .pyc file(s)"
    fi
    
    # Remove .pyo files
    PYO_COUNT=$(find . -type f -name "*.pyo" | wc -l)
    if [ $PYO_COUNT -gt 0 ]; then
        find . -type f -name "*.pyo" -delete 2>/dev/null
        colorize "$GREEN" "[+] Removed $PYO_COUNT .pyo file(s)"
    fi
    
    echo ""
    colorize "$GREEN$BOLD" "[+] Cleanup complete!"
    exit 0
fi

echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         Building r2s - Standalone Binary                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# Detect environment
ENV_TYPE=$(detect_environment)
colorize "$CYAN" "[*] Detected environment: ${BOLD}$ENV_TYPE${RESET}"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    colorize "$RED" "[-] Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check Python version (need 3.7+)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
colorize "$CYAN" "[*] Python version: $PYTHON_VERSION"

# Install/upgrade required packages
echo ""
colorize "$CYAN" "[*] Installing/upgrading dependencies..."
python3 -m pip install --upgrade pip setuptools wheel --quiet
python3 -m pip install -r requirements.txt --quiet

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    colorize "$CYAN" "[*] Installing PyInstaller..."
    python3 -m pip install pyinstaller --quiet
fi

# Clean previous builds
echo ""
colorize "$CYAN" "[*] Cleaning previous builds..."
rm -rf build/ dist/ *.spec __pycache__/ react2shell/__pycache__/

# Build with PyInstaller
echo ""
colorize "$CYAN" "[*] Building standalone binary with PyInstaller..."

# Build from modular structure
echo ""
echo -e "${CYAN}[*] Building from r2s_entry.py wrapper...${RESET}"
BUILD_TARGET="r2s_entry.py"

echo -e "${COFFEE}"
python3 -m PyInstaller \
    --name r2s \
    --onefile \
    --clean \
    --strip \
    --noupx \
    --console \
    --hidden-import=requests \
    --hidden-import=urllib3 \
    --hidden-import=charset_normalizer \
    --hidden-import=idna \
    --hidden-import=certifi \
    --hidden-import=concurrent.futures \
    --hidden-import=threading \
    --hidden-import=queue \
    --hidden-import=base64 \
    --hidden-import=json \
    --hidden-import=re \
    --hidden-import=random \
    --hidden-import=string \
    --hidden-import=time \
    --hidden-import=argparse \
    --hidden-import=sys \
    --hidden-import=os \
    --hidden-import=subprocess \
    --hidden-import=signal \
    --hidden-import=socket \
    --hidden-import=select \
    --hidden-import=struct \
    --hidden-import=binascii \
    --hidden-import=configparser \
    --hidden-import=readline \
    --hidden-import=react2shell \
    --hidden-import=react2shell.main \
    --hidden-import=react2shell.classes \
    --hidden-import=react2shell.classes.executor \
    --hidden-import=react2shell.classes.operations \
    --hidden-import=react2shell.classes.detector \
    --hidden-import=react2shell.classes.modules \
    --hidden-import=react2shell.classes.shell \
    --hidden-import=react2shell.services \
    --hidden-import=react2shell.services.logger \
    --hidden-import=react2shell.services.reporter \
    --hidden-import=react2shell.services.config \
    --hidden-import=react2shell.services.proxy \
    --hidden-import=react2shell.utils \
    --hidden-import=react2shell.utils.colors \
    --hidden-import=react2shell.utils.helpers \
    --collect-all requests \
    --collect-submodules react2shell \
    $BUILD_TARGET
echo -e "${RESET}"

# Check if build was successful
if [ -f "dist/r2s" ]; then
    echo ""
    colorize "$GREEN$BOLD" "[+] Build successful!"
    colorize "$CYAN" "[*] Binary location: $(pwd)/dist/r2s"
    
    # Make it executable
    chmod +x dist/r2s
    
    # Show binary size
    BINARY_SIZE=$(du -h dist/r2s | cut -f1)
    colorize "$CYAN" "[*] Binary size: $BINARY_SIZE"
    
    # Install binary based on detected environment
    install_binary "$ENV_TYPE" "dist/r2s"
    
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                    Build Complete!                        ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${RESET}"
else
    echo ""
    colorize "$RED" "[-] Build failed! Check the output above for errors."
    exit 1
fi

