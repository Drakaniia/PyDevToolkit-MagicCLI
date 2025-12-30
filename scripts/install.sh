#!/bin/bash

# ============================================================
# PyDevToolkit-MagicCLI Global Installer
# ============================================================
# Complete installation script that handles:
# - Python installation (if needed)
# - Package installation
# - Global command setup
# - Cross-platform support
# ============================================================

set -e  # Exit on error

# ============================================================
# CONFIGURATION
# ============================================================

PACKAGE_NAME="magic-cli"
PACKAGE_VERSION="1.0.0"
GITHUB_REPO="Drakaniia/PyDevToolkit-MagicCLI"
INSTALL_DIR="$HOME/.pydevtoolkit-magiccli"
PYTHON_VERSION="3.11.5"
MIN_PYTHON_VERSION="3.8.0"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ============================================================
# HELPER FUNCTIONS
# ============================================================

print_header() {
    clear
    echo -e "\n${BLUE}${BOLD}${NC}"
    echo -e "${BLUE}${BOLD}  PyDevToolkit-MagicCLI Global Installer                  ${NC}"
    echo -e "${BLUE}${BOLD}${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}${BOLD}${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
    echo -e "${CYAN}${NC}\n"
}

print_success() {
    echo -e "${GREEN}${NC} $1"
}

print_error() {
    echo -e "${RED}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"

    echo -e "${YELLOW}${prompt} [Y/n] (Y default):${NC} "

    read -r response

    if [ -z "$response" ]; then
        response="$default"
    fi

    case "$response" in
        [Yy]|[Yy][Ee][Ss]) return 0 ;;
        *) return 1 ;;
    esac
}

pause() {
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

# ============================================================
# SYSTEM DETECTION
# ============================================================

detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

detect_package_manager() {
    local os="$1"

    if [ "$os" = "linux" ]; then
        if command -v apt-get &> /dev/null; then
            echo "apt"
        elif command -v yum &> /dev/null; then
            echo "yum"
        elif command -v dnf &> /dev/null; then
            echo "dnf"
        elif command -v pacman &> /dev/null; then
            echo "pacman"
        else
            echo "unknown"
        fi
    elif [ "$os" = "macos" ]; then
        if command -v brew &> /dev/null; then
            echo "brew"
        else
            echo "none"
        fi
    else
        echo "none"
    fi
}

get_shell_config() {
    # Detect shell and return config file path
    local shell_name="$(basename "$SHELL")"

    case "$shell_name" in
        zsh)
            echo "$HOME/.zshrc"
            ;;
        bash)
            if [ -f "$HOME/.bashrc" ]; then
                echo "$HOME/.bashrc"
            elif [ -f "$HOME/.bash_profile" ]; then
                echo "$HOME/.bash_profile"
            else
                echo "$HOME/.bashrc"
            fi
            ;;
        fish)
            echo "$HOME/.config/fish/config.fish"
            ;;
        *)
            echo "$HOME/.bashrc"
            ;;
    esac
}

detect_shell() {
    basename "$SHELL" 2>/dev/null || echo "bash"
}

# ============================================================
# PYTHON DETECTION & INSTALLATION
# ============================================================

find_python_command() {
    # Try to find a working Python 3 command
    local commands=("python3" "python" "py")

    for cmd in "${commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            # Check if it's Python 3
            local version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)

            if [ "$major" = "3" ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done

    return 1
}

check_python_version() {
    local python_cmd="$1"
    local min_version="$2"

    local version=$("$python_cmd" --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)

    if [ -z "$version" ]; then
        return 1
    fi

    # Compare versions (simple comparison)
    local version_num=$(echo "$version" | sed 's/\.//g')
    local min_version_num=$(echo "$min_version" | sed 's/\.//g')

    if [ "$version_num" -ge "$min_version_num" ]; then
        return 0
    else
        return 1
    fi
}

install_python_linux() {
    local pkg_mgr="$1"

    case "$pkg_mgr" in
        apt)
            echo -e "${CYAN}Installing Python 3 on Ubuntu/Debian...${NC}"
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            ;;
        yum|dnf)
            echo -e "${CYAN}Installing Python 3 on CentOS/Fedora/RHEL...${NC}"
            sudo $pkg_mgr install -y python3 python3-pip
            ;;
        pacman)
            echo -e "${CYAN}Installing Python 3 on Arch Linux...${NC}"
            sudo pacman -S --noconfirm python python python-pip
            ;;
        *)
            print_error "Unsupported package manager. Please install Python 3.8+ manually."
            return 1
            ;;
    esac

    if command -v python3 &> /dev/null; then
        print_success "Python 3 installed successfully"
        return 0
    else
        print_error "Python 3 installation failed"
        return 1
    fi
}

install_python_macos() {
    local pkg_mgr="$1"

    if [ "$pkg_mgr" = "brew" ]; then
        echo -e "${CYAN}Installing Python 3 using Homebrew...${NC}"
        brew install python3
    else
        echo -e "${YELLOW}Homebrew not found. Installing Homebrew first...${NC}"
        # Try curl first, fallback to wget
        if command -v curl &> /dev/null; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        elif command -v wget &> /dev/null; then
            /bin/bash -c "$(wget -qO- https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            print_error "Neither curl nor wget is available. Please install one of them and try again."
            return 1
        fi

        echo -e "${CYAN}Installing Python 3 using Homebrew...${NC}"
        brew install python3
    fi

    if command -v python3 &> /dev/null; then
        print_success "Python 3 installed successfully"
        return 0
    else
        print_error "Python 3 installation failed"
        return 1
    fi
}

install_python_windows() {
    echo -e "${YELLOW}Installing Python 3 on Windows...${NC}"
    echo -e "${CYAN}This requires PowerShell with administrative privileges.${NC}"

    # Check if Chocolatey is installed
    if command -v choco &> /dev/null; then
        echo -e "${CYAN}Using Chocolatey to install Python...${NC}"
        if powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" 2>/dev/null; then
            if choco install -y python 2>/dev/null; then
                echo -e "${GREEN}Python installation completed successfully via Chocolatey${NC}"
            else
                print_error "Chocolatey installation of Python failed"
                return 1
            fi
        else
            print_error "Failed to install Chocolatey package manager"
            return 1
        fi
    else
        # Try to install Python via Windows package manager (winget) if available
        if command -v winget &> /dev/null; then
            echo -e "${CYAN}Using Windows Package Manager to install Python...${NC}"
            # First, check if winget is working properly
            if ! winget --info >/dev/null 2>&1; then
                print_error "Winget is installed but not functioning properly"
                echo -e "${YELLOW}Troubleshooting winget:${NC}"
                echo "  - Run 'winget --info' in an elevated PowerShell to diagnose"
                echo "  - You may need to reinstall winget or update Windows"
                echo "  - See: https://learn.microsoft.com/en-us/windows/package-manager/winget/"
                echo -e "${YELLOW}Attempting to install Python from web...${NC}"
                # Fallback to PowerShell script to download and install Python
                if powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe -OutFile python-installer.exe" 2>/dev/null; then
                    if powershell -Command "Start-Process -FilePath python-installer.exe -ArgumentList '/quiet', 'PrependPath=1' -Wait" 2>/dev/null; then
                        echo -e "${GREEN}Python installation completed via web download${NC}"
                    else
                        print_error "Failed to execute Python installer"
                        print_warning "Please try installing Python manually from https://www.python.org/downloads/"
                        if [ -f "python-installer.exe" ]; then
                            rm python-installer.exe
                        fi
                        return 1
                    fi
                else
                    print_error "Failed to download Python installer from web"
                    print_warning "Please check your internet connection and try installing Python manually from https://www.python.org/downloads/"
                    return 1
                fi

                # Clean up installer file
                if [ -f "python-installer.exe" ]; then
                    rm python-installer.exe
                fi
            elif winget install -e --id Python.Python.3 2>/dev/null || \
                 winget install -e --id "Python.Python.3" 2>/dev/null || \
                 winget install Python 2>/dev/null || \
                 winget install "Python 3" 2>/dev/null; then
                echo -e "${GREEN}Python installation completed successfully via winget${NC}"
            else
                echo -e "${RED}All winget installation attempts failed${NC}"
                echo -e "${YELLOW}Winget troubleshooting information:${NC}"

                # Display winget version and status
                echo -e "${CYAN}Winget version and status:${NC}"
                winget --info 2>/dev/null || echo "  - Winget not responding to --info command"

                # List available Python packages
                echo -e "${CYAN}Available Python packages in winget:${NC}"
                winget list python 2>/dev/null | head -10 || echo "  - No Python packages found or winget list command failed"

                # Show more detailed error troubleshooting
                echo -e "${CYAN}Possible solutions:${NC}"
                echo "  - Run Windows PowerShell as Administrator and execute: winget install Python.Python.3"
                echo "  - Update Windows to the latest version"
                echo "  - Reset winget: winget source reset"
                echo "  - Check Windows Package Manager version: winget --version"
                echo -e "  - Manually download from: https://www.python.org/downloads/"

                echo -e "${YELLOW}Attempting to install Python from web...${NC}"
                # Fallback to PowerShell script to download and install Python
                if powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe -OutFile python-installer.exe" 2>/dev/null; then
                    if powershell -Command "Start-Process -FilePath python-installer.exe -ArgumentList '/quiet', 'PrependPath=1' -Wait" 2>/dev/null; then
                        echo -e "${GREEN}Python installation completed via web download${NC}"
                    else
                        print_error "Failed to execute Python installer"
                        print_info "Detailed error information:"
                        echo "  - The downloaded installer file may be corrupted"
                        echo "  - Antivirus software may be blocking the installation"
                        echo "  - You may not have administrator privileges for installation"
                        echo "  - Try running this script in an elevated command prompt or PowerShell"
                        print_warning "Please try installing Python manually from https://www.python.org/downloads/"
                        if [ -f "python-installer.exe" ]; then
                            rm python-installer.exe
                        fi
                        return 1
                    fi
                else
                    print_error "Failed to download Python installer from web"
                    print_info "Detailed error information:"
                    echo "  - Check your internet connection"
                    echo "  - Firewall or proxy settings may be blocking access to python.org"
                    echo "  - PowerShell execution policy may be restricting downloads"
                    echo "  - Try running 'Invoke-WebRequest https://www.python.org' to test connectivity"
                    echo -e "  - You can manually download from: https://www.python.org/downloads/"
                    echo -e "  - Or try alternative Python download: https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
                    print_warning "If the issue persists, install Python manually from https://www.python.org/downloads/"
                    return 1
                fi

                # Clean up installer file
                if [ -f "python-installer.exe" ]; then
                    rm python-installer.exe
                fi
            fi
        else
            print_warning "Winget is not available on this system"
            echo -e "${YELLOW}Attempting to install Python from web...${NC}"
            # Fallback to PowerShell script to download and install Python
            if powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe -OutFile python-installer.exe" 2>/dev/null; then
                if powershell -Command "Start-Process -FilePath python-installer.exe -ArgumentList '/quiet', 'PrependPath=1' -Wait" 2>/dev/null; then
                    echo -e "${GREEN}Python installation completed via web download${NC}"
                else
                    print_error "Failed to execute Python installer"
                    print_info "Detailed error information:"
                    echo "  - The downloaded installer file may be corrupted"
                    echo "  - Antivirus software may be blocking the installation"
                    echo "  - You may not have administrator privileges for installation"
                    echo "  - Try running this script in an elevated command prompt or PowerShell"
                    print_warning "Please try installing Python manually from https://www.python.org/downloads/"
                    if [ -f "python-installer.exe" ]; then
                        rm python-installer.exe
                    fi
                    return 1
                fi
            else
                print_error "Failed to download Python installer from web"
                print_info "Detailed error information:"
                echo "  - Check your internet connection"
                echo "  - Firewall or proxy settings may be blocking access to python.org"
                echo "  - PowerShell execution policy may be restricting downloads"
                echo "  - Try running 'Invoke-WebRequest https://www.python.org' to test connectivity"
                echo -e "  - You can manually download from: https://www.python.org/downloads/"
                echo -e "  - Or try alternative Python download: https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
                print_warning "If the issue persists, install Python manually from https://www.python.org/downloads/"
                return 1
            fi

            # Clean up installer file
            if [ -f "python-installer.exe" ]; then
                rm python-installer.exe
            fi
        fi
    fi

    # For Git Bash, we need to verify installation
    # Wait a moment for the installation to complete
    sleep 5  # Increased sleep time to ensure installation completion

    # Check if Python is available (might require a new terminal session)
    if command -v python3 &> /dev/null || command -v python &> /dev/null; then
        # Verify Python version meets requirements
        if PYTHON_CMD=$(find_python_command); then
            PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
            print_success "Python 3 found: $PYTHON_CMD ($PYTHON_VERSION)"

            # Verify minimum version
            PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
            PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")

            if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
                print_success "Python version meets requirements (>= $MIN_PYTHON_VERSION)"
                return 0
            else
                print_error "Installed Python version is too old: $PYTHON_VERSION"
                print_error "Python $MIN_PYTHON_VERSION or higher is required"
                return 1
            fi
        else
            print_error "Python was installed but cannot be found in PATH"
            print_info "Please restart your terminal and run this setup script again"
            print_info "If the problem persists, verify Python is installed and in your PATH environment variable"
            return 1
        fi
    else
        print_error "Python installation appears to have failed or is not accessible"
        print_info "Please restart your terminal and run this setup script again"
        print_info "If the issue persists, check that:"
        echo "  - Python was installed successfully"
        echo "  - Python was added to your PATH environment variable"
        echo "  - You have appropriate permissions to access Python"
        echo -e "  - You may need to install Python manually from https://www.python.org/downloads/"
        return 1  # Return 1 to indicate that setup should not continue
    fi
}

setup_python() {
    print_section "Python Setup"

    # Try to find existing Python
    if PYTHON_CMD=$(find_python_command); then
        print_success "Found Python 3 command: $PYTHON_CMD"

        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
        print_info "Python version: $PYTHON_VERSION"

        if check_python_version "$PYTHON_CMD" "$MIN_PYTHON_VERSION"; then
            print_success "Python version meets requirements (>= $MIN_PYTHON_VERSION)"
        else
            print_warning "Python version is too old: $PYTHON_VERSION"
            print_info "Minimum required version: $MIN_PYTHON_VERSION"

            if ask_yes_no "Would you like to install a newer version of Python?"; then
                local os=$(detect_os)
                local pkg_mgr=$(detect_package_manager "$os")

                case "$os" in
                    linux)
                        if install_python_linux "$pkg_mgr"; then
                            PYTHON_CMD=$(find_python_command)
                        else
                            print_error "Failed to install Python"
                            return 1
                        fi
                        ;;
                    macos)
                        if install_python_macos "$pkg_mgr"; then
                            PYTHON_CMD=$(find_python_command)
                        else
                            print_error "Failed to install Python"
                            return 1
                        fi
                        ;;
                    windows)
                        if install_python_windows; then
                            PYTHON_CMD=$(find_python_command)
                        else
                            print_error "Failed to install Python"
                            return 1
                        fi
                        ;;
                    *)
                        print_error "Unsupported operating system: $os"
                        print_info "Please install Python $MIN_PYTHON_VERSION+ manually"
                        return 1
                        ;;
                esac
            else
                print_error "Python $MIN_PYTHON_VERSION+ is required"
                return 1
            fi
        fi
    else
        print_warning "Python 3 not found on this system"

        if ask_yes_no "Would you like to install Python automatically?"; then
            local os=$(detect_os)
            local pkg_mgr=$(detect_package_manager "$os")

            case "$os" in
                linux)
                    if install_python_linux "$pkg_mgr"; then
                        PYTHON_CMD=$(find_python_command)
                    else
                        print_error "Failed to install Python"
                        return 1
                    fi
                    ;;
                macos)
                    if install_python_macos "$pkg_mgr"; then
                        PYTHON_CMD=$(find_python_command)
                    else
                        print_error "Failed to install Python"
                        return 1
                    fi
                    ;;
                windows)
                    if install_python_windows; then
                        PYTHON_CMD=$(find_python_command)
                    else
                        print_error "Failed to install Python"
                        return 1
                    fi
                    ;;
                *)
                    print_error "Unsupported operating system: $os"
                    print_info "Please install Python $MIN_PYTHON_VERSION+ manually from https://www.python.org/downloads/"
                    return 1
                    ;;
            esac
        else
            print_error "Python 3.8+ is required for PyDevToolkit-MagicCLI"
            print_info "Please install Python manually and run this installer again"
            return 1
        fi
    fi

    # Verify pip
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_success "pip is available"
    else
        print_warning "pip is not available - installing..."
        if $PYTHON_CMD -m ensurepip --upgrade &> /dev/null; then
            print_success "pip installed successfully"
        else
            print_error "Failed to install pip"
            return 1
        fi
    fi

    # Upgrade pip
    if $PYTHON_CMD -m pip install --upgrade pip &> /dev/null; then
        print_success "pip upgraded to latest version"
    else
        print_warning "Could not upgrade pip (continuing anyway)"
    fi

    return 0
}

# ============================================================
# PACKAGE INSTALLATION
# ============================================================

install_package() {
    print_section "Package Installation"

    # Create installation directory
    mkdir -p "$INSTALL_DIR"

    print_info "Installing PyDevToolkit-MagicCLI..."

    # Try PyPI first, fallback to GitHub
    if $PYTHON_CMD -m pip install "$PACKAGE_NAME" 2>/dev/null; then
        print_success "Package installed from PyPI"
    else
        print_info "PyPI installation failed, trying GitHub..."

        if $PYTHON_CMD -m pip install "git+https://github.com/$GITHUB_REPO.git" 2>/dev/null; then
            print_success "Package installed from GitHub"
        else
            print_error "Failed to install package from both PyPI and GitHub"
            print_info "Please check your internet connection and try again"
            return 1
        fi
    fi

    # Verify installation
    if $PYTHON_CMD -c "import src.main; print('Package imported successfully')" 2>/dev/null; then
        print_success "Package verification passed"
    else
        print_warning "Package import test failed (this may be normal)"
    fi

    return 0
}

# ============================================================
# COMMAND SETUP
# ============================================================

setup_command() {
    print_section "Command Setup"

    local shell_config=$(get_shell_config)
    local shell_type=$(detect_shell)

    print_info "Detected shell: $shell_type"
    print_info "Config file: $shell_config"

    # Create bin directory if needed
    mkdir -p "$INSTALL_DIR/bin"

    # Create wrapper script
    local wrapper_script="$INSTALL_DIR/bin/magic"

    cat > "$wrapper_script" << EOF
#!/bin/bash
# PyDevToolkit-MagicCLI Wrapper Script
# Generated by installer on $(date)

# Find Python command
PYTHON_CMDS=("python3" "python" "py")
PYTHON_CMD=""

for cmd in "\${PYTHON_CMDS[@]}"; do
    if command -v "\$cmd" &> /dev/null; then
        # Check if it's Python 3
        if "\$cmd" -c "import sys; sys.exit(0 if sys.version_info.major >= 3 else 1)" 2>/dev/null; then
            PYTHON_CMD="\$cmd"
            break
        fi
    fi
done

if [ -z "\$PYTHON_CMD" ]; then
    echo "Error: Python 3 not found. Please reinstall PyDevToolkit-MagicCLI."
    exit 1
fi

# Run the magic command
exec "\$PYTHON_CMD" -m src.main "\$@"
EOF

    chmod +x "$wrapper_script"
    print_success "Created wrapper script: $wrapper_script"

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$INSTALL_DIR/bin:"* ]]; then
        # Backup existing config
        if [ -f "$shell_config" ]; then
            cp "$shell_config" "${shell_config}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        fi

        # Remove existing PATH entries for our install dir
        sed -i '/export PATH=.*pydevtoolkit-magiccli/d' "$shell_config" 2>/dev/null || true

        # Add new PATH entry
        echo "" >> "$shell_config"
        echo "# PyDevToolkit-MagicCLI" >> "$shell_config"
        echo "export PATH=\"$INSTALL_DIR/bin:\$PATH\"" >> "$shell_config"
        echo "" >> "$shell_config"

        print_success "Added PyDevToolkit-MagicCLI to PATH in $shell_config"
        print_info "Please restart your terminal or run: source $shell_config"
    else
        print_info "PyDevToolkit-MagicCLI already in PATH"
    fi

    return 0
}

# ============================================================
# VERIFICATION
# ============================================================

verify_installation() {
    print_section "Verification"

    # Test if magic command is available
    if command -v magic &> /dev/null; then
        print_success "'magic' command is available"
    else
        print_warning "'magic' command not found in current session"
        print_info "Please restart your terminal or run: source $(get_shell_config)"
    fi

    # Test package import
    if $PYTHON_CMD -c "import src.main" 2>/dev/null; then
        print_success "Package can be imported"
    else
        print_error "Package import failed"
        return 1
    fi

    return 0
}

# ============================================================
# MAIN INSTALLATION FLOW
# ============================================================

main() {
    print_header

    echo -e "${CYAN}This installer will:${NC}"
    echo -e "  • Install Python 3.8+ (if needed)"
    echo -e "  • Install PyDevToolkit-MagicCLI package"
    echo -e "  • Set up the 'magic' command globally"
    echo -e "  • Configure your shell environment"
    echo ""

    if ! ask_yes_no "Ready to begin installation?"; then
        echo ""
        echo -e "${YELLOW}Installation cancelled by user.${NC}"
        exit 0
    fi

    # Setup Python
    if ! setup_python; then
        print_error "Python setup failed"
        exit 1
    fi

    # Install package
    if ! install_package; then
        print_error "Package installation failed"
        exit 1
    fi

    # Setup command
    if ! setup_command; then
        print_error "Command setup failed"
        exit 1
    fi

    # Verify installation
    if ! verify_installation; then
        print_error "Installation verification failed"
        exit 1
    fi

    print_section "Installation Complete!"

    echo -e "${GREEN}${BOLD}PyDevToolkit-MagicCLI has been installed successfully!${NC}"
    echo ""
    echo -e "${CYAN}Installation Summary:${NC}"
    echo -e "  ${GREEN}[OK]${NC} Python: $PYTHON_CMD"
    echo -e "  ${GREEN}[OK]${NC} Package: $PACKAGE_NAME"
    echo -e "  ${GREEN}[OK]${NC} Command: magic"
    echo -e "  ${GREEN}[OK]${NC} Location: $INSTALL_DIR"
    echo ""

    echo -e "${YELLOW}${BOLD}IMPORTANT: Terminal Restart Required${NC}"
    echo -e "${YELLOW}The 'magic' command will NOT work until you:${NC}"
    echo ""
    echo -e "${RED}REQUIRED - Choose ONE option:${NC}"
    echo -e "  ${BLUE}1.${NC} ${BOLD}RESTART TERMINAL (Recommended)${NC}"
    echo -e "     • Close this terminal completely"
    echo -e "     • Open a new terminal window"
    echo -e "     • Type: ${GREEN}magic${NC}"
    echo ""
    echo -e "  ${BLUE}2.${NC} ${BOLD}RELOAD SHELL (May not work in all terminals)${NC}"
    echo -e "     • Type: ${GREEN}source $(get_shell_config)${NC}"
    echo -e "     • Then try: ${GREEN}magic${NC}"
    echo ""

    echo -e "${CYAN}${BOLD}Quick Start Guide:${NC}"
    echo -e "  • ${BLUE}Git Operations:${NC} Push, pull, commit management"
    echo -e "  • ${BLUE}Project Structure:${NC} View and navigate directories"
    echo -e "  • ${BLUE}Web Development:${NC} Modern frontend/backend automation"
    echo -e "  • ${BLUE}And much more!${NC}"
    echo ""

    echo -e "${CYAN}${BOLD}Uninstall:${NC}"
    echo -e "  • Run: ${GREEN}bash uninstall.sh${NC}"
    echo ""

    echo -e "${GREEN}${NC}\n"
}

# ============================================================
# ERROR HANDLING
# ============================================================

# Trap errors
trap 'echo -e "\n${RED}${BOLD}Installation failed. Please check the errors above.${NC}\n"; exit 1' ERR

# Trap Ctrl+C
trap 'echo -e "\n\n${YELLOW}Installation cancelled by user.${NC}\n"; exit 130' INT

# ============================================================
# ENTRY POINT
# ============================================================

main "$@"