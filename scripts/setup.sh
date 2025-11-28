#!/bin/bash

# ============================================================
# Python Automation System - Complete Setup Script
# ============================================================
# Features:
# - Python installation detection and guidance
# - Comprehensive system validation
# - Automatic shell configuration (bash, zsh, fish)
# - Git setup with user configuration
# - Intelligent PATH detection and configuration
# - Backup and rollback capabilities
# - Cross-platform support (Linux, macOS, Windows/Git Bash)
# - Test installation functionality
# - Interactive and non-interactive modes
# ============================================================

set -e  # Exit on error

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MAIN_PY="$PROJECT_ROOT/src/main.py"
MIN_PYTHON_VERSION="3.7"
COMMAND_ALIAS="magic"

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
    echo -e "${BLUE}${BOLD}  Python Automation System - Complete Setup Wizard            ${NC}"
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

print_step() {
    echo -e "\n${MAGENTA}${NC} ${BOLD}$1${NC}"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    
    if [ "$default" = "y" ]; then
        echo -e "${YELLOW}${prompt} [Y/n]:${NC} "
    else
        echo -e "${YELLOW}${prompt} [y/N]:${NC} "
    fi
    
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
# PYTHON DETECTION & INSTALLATION GUIDANCE
# ============================================================

find_python_command() {
    # Try to find a working Python 3 command
    local commands=("python3" "python" "py")
    
    for cmd in "${commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            # Check if it's Python 3
            local version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)
            
            if [ "$major" = "3" ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    
    return 1
}

validate_python() {
    print_section "Python Detection & Validation"
    
    # Try to find Python
    if PYTHON_CMD=$(find_python_command); then
        print_success "Found Python 3 command: $PYTHON_CMD"
    else
        print_error "Python 3 not found on this system"
        echo ""
        offer_python_installation
        return 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
    print_info "Python version: $PYTHON_VERSION"
    
    # Verify minimum version
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
        print_error "Python $MIN_PYTHON_VERSION or higher is required"
        print_info "Current version: $PYTHON_VERSION"
        echo ""
        offer_python_installation
        return 1
    fi
    
    print_success "Python version meets requirements (>= $MIN_PYTHON_VERSION)"
    
    # Test Python execution
    if $PYTHON_CMD -c "import sys; sys.exit(0)" &> /dev/null; then
        print_success "Python execution test passed"
    else
        print_error "Python execution test failed"
        return 1
    fi
    
    # Check pip
    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_success "pip is available"
    else
        print_warning "pip is not available"
        print_info "Some features may require pip for dependency installation"
    fi
    
    echo ""
    return 0
}

install_python_linux() {
    local pkg_mgr=$(detect_package_manager "$(detect_os)")

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
            echo -e "${RED}Unsupported package manager. Please install Python 3.7+ manually.${NC}"
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
    local pkg_mgr=$(detect_package_manager "$(detect_os)")

    if [ "$pkg_mgr" = "brew" ]; then
        echo -e "${CYAN}Installing Python 3 using Homebrew...${NC}"
        brew install python3
    else
        echo -e "${YELLOW}Homebrew not found. Installing Homebrew first...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

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
        powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        choco install -y python
    else
        # Try to install Python via Windows package manager (winget) if available
        if command -v winget &> /dev/null; then
            echo -e "${CYAN}Using Windows Package Manager to install Python...${NC}"
            winget install -e --id Python.Python.3
        else
            # Fallback to PowerShell script to download and install Python
            echo -e "${YELLOW}Please download and install Python from: https://www.python.org/downloads/${NC}"
            echo -e "${YELLOW}Make sure to check 'Add Python to PATH' during installation.${NC}"
            echo -e "${CYAN}After installation, please restart your terminal and run this setup script again.${NC}"
            return 1
        fi
    fi

    # For Git Bash, we need to verify installation
    # Wait a moment for the installation to complete
    sleep 3

    # Check if Python is available (might require a new terminal session)
    if command -v python3 &> /dev/null || command -v python &> /dev/null; then
        print_success "Python 3 installation completed"
        return 0
    else
        print_warning "Python might require terminal restart to be available"
        print_info "Please restart your terminal and run this setup script again"
        return 0  # Return 0 since installation likely succeeded but needs restart
    fi
}

offer_python_installation() {
    local os=$(detect_os)

    echo -e "${RED}${BOLD}Python 3 is required but not found!${NC}\n"

    if ask_yes_no "Would you like to automatically install Python 3?"; then
        echo ""

        case "$os" in
            linux)
                if install_python_linux; then
                    print_success "Python 3 installation completed successfully!"
                    echo -e "${CYAN}Verifying installation...${NC}"

                    # Try to find the newly installed Python
                    if PYTHON_CMD=$(find_python_command); then
                        print_success "Found Python command: $PYTHON_CMD"
                        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
                        print_success "Python version: $PYTHON_VERSION"

                        # Verify minimum version
                        PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
                        PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

                        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
                            print_error "Installed Python version is too old: $PYTHON_VERSION"
                            print_error "Python $MIN_PYTHON_VERSION or higher is required"
                            exit 1
                        fi

                        print_success "Python installation verified and meets requirements"
                        return 0  # Success - continue with setup
                    else
                        print_error "Python was installed but cannot be found in PATH"
                        print_info "Please restart your terminal and run this setup script again"
                        exit 1
                    fi
                else
                    print_error "Python installation failed"
                    echo -e "${YELLOW}Please install Python 3.7+ manually.${NC}"
                    exit 1
                fi
                ;;
            macos)
                if install_python_macos; then
                    print_success "Python 3 installation completed successfully!"
                    echo -e "${CYAN}Verifying installation...${NC}"

                    # Refresh PATH to include new Python installation
                    export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

                    if PYTHON_CMD=$(find_python_command); then
                        print_success "Found Python command: $PYTHON_CMD"
                        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
                        print_success "Python version: $PYTHON_VERSION"

                        # Verify minimum version
                        PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
                        PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

                        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
                            print_error "Installed Python version is too old: $PYTHON_VERSION"
                            print_error "Python $MIN_PYTHON_VERSION or higher is required"
                            exit 1
                        fi

                        print_success "Python installation verified and meets requirements"
                        return 0  # Success - continue with setup
                    else
                        print_error "Python was installed but cannot be found in PATH"
                        print_info "Please restart your terminal and run this setup script again"
                        exit 1
                    fi
                else
                    print_error "Python installation failed"
                    echo -e "${YELLOW}Please install Python 3.7+ manually.${NC}"
                    exit 1
                fi
                ;;
            windows)
                if install_python_windows; then
                    print_success "Python installation completed!"
                    print_info "Please restart your terminal and run this setup script again"
                    print_info "The new terminal will recognize the installed Python"
                    exit 0  # Exit this setup run, user needs to restart terminal
                else
                    print_error "Python installation failed"
                    echo -e "${YELLOW}Please install Python 3.7+ manually from https://www.python.org/downloads/${NC}"
                    exit 1
                fi
                ;;
            *)
                print_error "Unsupported operating system: $os"
                echo -e "${YELLOW}Please install Python 3.7+ manually.${NC}"
                exit 1
                ;;
        esac
    else
        echo -e "${YELLOW}Python 3.7+ is required for this application.${NC}"
        echo -e "${YELLOW}Please install it manually and run this setup script again.${NC}"
        echo ""
        echo -e "${CYAN}You can download Python from: https://www.python.org/downloads/${NC}"
        exit 1
    fi
}

# ============================================================
# GIT VALIDATION & CONFIGURATION
# ============================================================

validate_git() {
    print_section "Git Validation & Configuration"
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        echo ""
        offer_git_installation
        return 1
    fi
    
    GIT_VERSION=$(git --version 2>&1)
    print_success "Git is installed: $GIT_VERSION"
    
    # Check git config
    GIT_USER=$(git config --global user.name 2>/dev/null || echo "")
    GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")
    
    if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
        print_warning "Git user configuration incomplete"
        echo ""
        
        if ask_yes_no "Would you like to configure Git now?"; then
            configure_git_user
        else
            print_info "You can configure Git later with:"
            print_info "  git config --global user.name 'Your Name'"
            print_info "  git config --global user.email 'your@email.com'"
        fi
    else
        print_success "Git user configured: $GIT_USER <$GIT_EMAIL>"
    fi
    
    echo ""
    return 0
}

offer_git_installation() {
    local os=$(detect_os)
    local pkg_mgr=$(detect_package_manager "$os")
    
    echo -e "${YELLOW}Git Installation Instructions:${NC}\n"
    
    case "$os" in
        linux)
            case "$pkg_mgr" in
                apt)
                    echo "Ubuntu/Debian:"
                    echo "  sudo apt update"
                    echo "  sudo apt install git"
                    ;;
                yum|dnf)
                    echo "CentOS/Fedora/RHEL:"
                    echo "  sudo $pkg_mgr install git"
                    ;;
                pacman)
                    echo "Arch Linux:"
                    echo "  sudo pacman -S git"
                    ;;
            esac
            ;;
        macos)
            if [ "$pkg_mgr" = "brew" ]; then
                echo "Using Homebrew:"
                echo "  brew install git"
            else
                echo "Install Xcode Command Line Tools:"
                echo "  xcode-select --install"
            fi
            ;;
        windows)
            echo "Download from: https://git-scm.com/download/win"
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}Git is optional but recommended for full functionality.${NC}"
    echo ""
    
    if ! ask_yes_no "Continue without Git?" "n"; then
        exit 1
    fi
}

configure_git_user() {
    echo ""
    echo -e "${CYAN}Git User Configuration${NC}"
    echo -e "${CYAN}${NC}"
    echo ""
    
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    
    if [ -n "$git_name" ] && [ -n "$git_email" ]; then
        git config --global user.name "$git_name"
        git config --global user.email "$git_email"
        print_success "Git configured: $git_name <$git_email>"
    else
        print_error "Invalid input. Git configuration skipped."
    fi
    
    echo ""
}

# ============================================================
# DEPENDENCY INSTALLATION
# ============================================================

install_dependencies() {
    print_section "Installing Python Dependencies"

    # Change to project root for installation
    cd "$PROJECT_ROOT"

    # Check if requirements.txt exists
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_info "Found requirements.txt, installing dependencies..."

        if $PYTHON_CMD -m pip install --upgrade pip; then
            print_success "Updated pip"
        else
            print_error "Failed to update pip, attempting to continue..."
        fi

        if $PYTHON_CMD -m pip install -r "$PROJECT_ROOT/requirements.txt"; then
            print_success "Successfully installed all dependencies"
        else
            print_error "Failed to install dependencies"
            echo ""
            print_info "Trying alternative installation with --user flag..."
            if $PYTHON_CMD -m pip install --user -r "$PROJECT_ROOT/requirements.txt"; then
                print_success "Successfully installed dependencies with --user flag"
            else
                print_error "Failed to install dependencies with --user flag"
                echo -e "${YELLOW}You may need to install dependencies manually later.${NC}"
            fi
        fi
    else
        # Fallback to setup.py if requirements.txt doesn't exist
        print_info "Installing from setup.py..."

        if $PYTHON_CMD -m pip install --upgrade pip; then
            print_success "Updated pip"
        else
            print_error "Failed to update pip, attempting to continue..."
        fi

        if $PYTHON_CMD -m pip install -e .; then
            print_success "Successfully installed from setup.py"
        else
            print_error "Failed to install from setup.py"
            echo -e "${YELLOW}You may need to install dependencies manually later.${NC}"
        fi
    fi

    echo ""
}

# ============================================================
# FILE STRUCTURE VALIDATION
# ============================================================

validate_files() {
    print_section "File Structure Validation"

    local all_valid=true

    # Check main.py
    if [ -f "$MAIN_PY" ]; then
        print_success "Found main.py"
    else
        print_error "main.py not found at: $MAIN_PY"
        all_valid=false
    fi

    # Check requirements.txt
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_success "Found requirements.txt"
    else
        print_info "Note: requirements.txt not found, will install from setup.py"
    fi

    # Check src directory
    if [ -d "$PROJECT_ROOT/src" ]; then
        print_success "Found src/ directory"
    else
        print_error "src/ directory not found"
        all_valid=false
    fi

    # Check critical modules
    local critical_modules=(
        "src/__init__.py"
        "src/menu.py"
        "src/modules/git_operations/menu.py"
        "src/modules/project_management/folder_navigator.py"
    )

    for module in "${critical_modules[@]}"; do
        if [ -f "$PROJECT_ROOT/$module" ]; then
            print_success "Found $module"
        else
            print_error "Missing critical module: $module"
            all_valid=false
        fi
    done

    echo ""

    if [ "$all_valid" = false ]; then
        print_error "File structure validation failed"
        echo ""
        echo -e "${RED}The installation appears to be incomplete or corrupted.${NC}"
        echo -e "${YELLOW}Please ensure all files are present before continuing.${NC}"
        echo ""
        exit 1
    fi

    return 0
}

# ============================================================
# PERMISSIONS
# ============================================================

validate_permissions() {
    print_section "Permission Configuration"
    
    # Make main.py executable
    if chmod +x "$MAIN_PY" 2>/dev/null; then
        print_success "Set executable permissions on main.py"
    else
        print_warning "Could not set executable permissions (may not be needed on Windows)"
    fi
    
    # Make bin/magic executable if it exists
    if [ -f "$PROJECT_ROOT/bin/magic" ]; then
        if chmod +x "$PROJECT_ROOT/bin/magic" 2>/dev/null; then
            print_success "Set executable permissions on bin/magic"
        else
            print_warning "Could not set executable permissions on bin/magic"
        fi
    fi
    
    # Check write permissions on shell config
    local shell_config=$(get_shell_config)
    local shell_config_dir=$(dirname "$shell_config")
    
    # Create config directory if needed
    if [ ! -d "$shell_config_dir" ]; then
        if mkdir -p "$shell_config_dir" 2>/dev/null; then
            print_success "Created config directory: $shell_config_dir"
        else
            print_error "Cannot create config directory: $shell_config_dir"
            echo ""
            echo -e "${RED}You may need elevated permissions.${NC}"
            exit 1
        fi
    fi
    
    # Create config file if it doesn't exist
    if [ ! -f "$shell_config" ]; then
        if touch "$shell_config" 2>/dev/null; then
            print_success "Created shell config: $shell_config"
        fi
    fi
    
    if [ -w "$shell_config" ]; then
        print_success "Shell config is writable: $shell_config"
    else
        print_error "Cannot write to shell config: $shell_config"
        echo ""
        echo -e "${RED}You may need to run with appropriate permissions.${NC}"
        exit 1
    fi
    
    echo ""
}

# ============================================================
# SHELL CONFIGURATION
# ============================================================

backup_shell_config() {
    local config_file="$1"
    local backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [ -f "$config_file" ]; then
        if cp "$config_file" "$backup_file" 2>/dev/null; then
            print_success "Created backup: $(basename "$backup_file")"
            echo "$backup_file"  # Return backup path
            return 0
        else
            print_warning "Could not create backup"
            return 1
        fi
    fi
}

configure_shell_alias() {
    print_section "Shell Alias Configuration"
    
    local shell_config=$(get_shell_config)
    local shell_type=$(detect_shell)
    
    print_info "Detected shell: $shell_type"
    print_info "Config file: $shell_config"
    echo ""
    
    # Backup existing config
    local backup_path=$(backup_shell_config "$shell_config")
    
    # Remove existing alias (if any) - using the working approach from fix scripts
    sed -i '/# PyDevToolkit MagicCLI/,+3d' "$shell_config" 2>/dev/null || true
    
    # Build alias command based on working fix scripts for Windows Git Bash
    local alias_cmd=""
    local os=$(detect_os)
    
    if [ "$os" = "windows" ]; then
        # Windows Git Bash specific fix - convert Windows path to Git Bash format
        local git_bash_path=$(echo "$PROJECT_ROOT" | sed 's|C:|/c|g' | sed 's|\\|/|g')
        alias_cmd="alias magic='python \"$git_bash_path/src/main.py\" \"\$@\"'"
    else
        # Unix-like systems
        if [ -f "$PROJECT_ROOT/bin/magic" ]; then
            case "$shell_type" in
                fish)
                    alias_cmd="alias $COMMAND_ALIAS='set PYTHONIOENCODING=utf-8 && \"$PROJECT_ROOT/bin/magic\"'"
                    ;;
                *)
                    alias_cmd="alias $COMMAND_ALIAS='PYTHONIOENCODING=utf-8 \"$PROJECT_ROOT/bin/magic\"'"
                    ;;
            esac
        else
            case "$shell_type" in
                fish)
                    alias_cmd="alias $COMMAND_ALIAS='set PYTHONIOENCODING=utf-8 && $PYTHON_CMD \"$MAIN_PY\"'"
                    ;;
                *)
                    alias_cmd="alias $COMMAND_ALIAS='PYTHONIOENCODING=utf-8 $PYTHON_CMD \"$MAIN_PY\"'"
                    ;;
            esac
        fi
    fi
    
    # Add new alias using the working format from fix scripts
    {
        echo ""
        echo "# ============================================"
        echo "# PyDevToolkit MagicCLI"
        echo "# Fixed setup: $(date)"
        echo "# ============================================"
        echo "$alias_cmd"
        echo ""
    } >> "$shell_config"
    
    print_success "Added '$COMMAND_ALIAS' alias to $shell_config"
    print_info "Command: $alias_cmd"
    echo ""
    
    # Show rollback instructions
    if [ -n "$backup_path" ]; then
        print_info "Backup saved to: $backup_path"
        print_info "To rollback: cp \"$backup_path\" \"$shell_config\""
        echo ""
    fi
}


# ============================================================
# FINAL COMPLETION
# ============================================================

clear_terminal_cache() {
    print_step "Clearing Terminal Cache"
    
    # Clear command hash table
    hash -r 2>/dev/null || true
    
    # Clear any potential Python cache
    if [ -d "$PROJECT_ROOT/__pycache__" ]; then
        rm -rf "$PROJECT_ROOT/__pycache__" 2>/dev/null || true
        print_info "Cleared Python cache"
    fi
    
    # Clear any potential pip cache issues
    $PYTHON_CMD -m pip cache purge 2>/dev/null || true
    
    print_success "Terminal cache cleared"
}

print_completion_message() {
    print_section "Setup Complete!"
    
    echo -e "${GREEN}${BOLD}${NC}"
    echo -e "${GREEN}${BOLD}  PyDevToolkit MagicCLI is ready to use!                      ${NC}"
    echo -e "${GREEN}${BOLD}${NC}"
    
    echo -e "\n${CYAN}${BOLD}Installation Summary:${NC}"
    echo -e "  ${GREEN}[OK]${NC} Python: $PYTHON_CMD ($PYTHON_VERSION)"
    echo -e "  ${GREEN}[OK]${NC} Install location: $PROJECT_ROOT"
    echo -e "  ${GREEN}[OK]${NC} Shell config: $(get_shell_config)"
    echo -e "  ${GREEN}[OK]${NC} Command alias: ${YELLOW}${BOLD}$COMMAND_ALIAS${NC}"
    
    echo -e "\n${YELLOW}${BOLD}IMPORTANT: Terminal Restart Required${NC}"
    echo -e "${YELLOW}The '$COMMAND_ALIAS' command will NOT work until you:${NC}"
    echo ""
    
    echo -e "${CYAN}${BOLD}REQUIRED - Choose ONE option:${NC}"
    echo -e "  ${RED}1.${NC} ${BOLD}RESTART TERMINAL (Recommended)${NC}"
    echo -e "     • Close this terminal completely"
    echo -e "     • Open a new terminal window"
    echo -e "     • Type: ${YELLOW}$COMMAND_ALIAS${NC}"
    echo ""
    
    echo -e "  ${RED}2.${NC} ${BOLD}RELOAD SHELL (May not work in all terminals)${NC}"
    echo -e "     • Type: ${YELLOW}source $(get_shell_config)${NC}"
    echo -e "     • Then: ${YELLOW}hash -r${NC}"
    echo -e "     • Try: ${YELLOW}$COMMAND_ALIAS${NC}"
    echo ""
    
    if [ "$(detect_os)" = "windows" ]; then
        echo -e "  ${RED}3.${NC} ${BOLD}IDE USERS (VS Code, etc.)${NC}"
        echo -e "     • Save all files"
        echo -e "     • Close terminal panel (${YELLOW}Ctrl+Shift+\`${NC})"
        echo -e "     • Open new terminal (${YELLOW}Ctrl+Shift+\`${NC})"
        echo -e "     • Try: ${YELLOW}$COMMAND_ALIAS${NC}"
        echo ""
    fi
    
    echo -e "${CYAN}${BOLD}Quick Start Guide:${NC}"
    echo -e "  • ${BLUE}GitHub Operations:${NC} Push, pull, commit management"
    echo -e "  • ${BLUE}Project Management:${NC} View structure, navigate folders"
    echo -e "  • ${BLUE}Web Development:${NC} Modern frontend project automation"
    echo -e "  • ${BLUE}Backend Development:${NC} API scaffolding, database tools"
    
    echo -e "\n${CYAN}${BOLD}Resources:${NC}"
    echo -e "  • README: $PROJECT_ROOT/README.md"
    echo -e "  • Repository: https://github.com/Drakaniia/PyDevToolkit-MagicCLI"
    echo -e "  • Issues: https://github.com/Drakaniia/PyDevToolkit-MagicCLI/issues"
    
    echo -e "\n${CYAN}${BOLD}Need Help?${NC}"
    echo -e "  • Email: alistairybaez574@gmail.com"
    echo -e "  • Documentation: Check README.md for detailed usage"
    
    echo -e "\n${GREEN}${NC}\n"
}

reload_shell_config() {
    local shell_config=$(get_shell_config)
    
    echo ""
    print_step "Shell Configuration Reload Options"
    echo ""
    
    echo -e "${CYAN}The shell configuration has been updated, but the current session needs to be refreshed.${NC}"
    echo ""
    
    # Option 1: Try to reload the current shell
    if ask_yes_no "Option 1: Reload current shell configuration now?"; then
        if [ -f "$shell_config" ]; then
            print_info "Reloading $shell_config..."
            
            # Source the config
            set +e  # Don't exit on error for sourcing
            # shellcheck disable=SC1090
            source "$shell_config" 2>/dev/null || true
            set -e
            
            # Clear command hash cache
            hash -r 2>/dev/null || true
            
            print_success "Configuration reloaded!"
            print_success "Command cache cleared!"
            echo ""
            print_info "You should now be able to use: ${YELLOW}${BOLD}$COMMAND_ALIAS${NC}"
            
            # Test if the alias is now available
            if command -v "$COMMAND_ALIAS" &> /dev/null || alias "$COMMAND_ALIAS" &> /dev/null; then
                print_success "'$COMMAND_ALIAS' command is now available!"
                echo ""
                echo -e "${CYAN}${BOLD}Try it now:${NC}"
                echo -e "  ${YELLOW}$COMMAND_ALIAS${NC}"
            else
                print_warning "Alias not detected in current session"
                print_info "This sometimes happens in Git Bash - restarting is recommended"
                echo ""
                offer_restart_options
            fi
        else
            print_warning "Could not reload configuration"
            print_info "Please restart your terminal or run: source $shell_config"
            offer_restart_options
        fi
    else
        offer_restart_options
    fi
    
    echo ""
}

offer_restart_options() {
    local shell_config=$(get_shell_config)
    local os=$(detect_os)
    
    echo ""
    print_step "Alternative Restart Options"
    echo ""
    
    echo -e "${YELLOW}To ensure the '$COMMAND_ALIAS' command works, choose one of these options:${NC}"
    echo ""
    
    echo -e "${BLUE}Option A: Restart Terminal (Recommended)${NC}"
    echo -e "  • Close this terminal window"
    echo -e "  • Open a new terminal"
    echo -e "  • Type: ${YELLOW}$COMMAND_ALIAS${NC}"
    echo ""
    
    echo -e "${BLUE}Option B: Manual Reload${NC}"
    echo -e "  • Run: ${YELLOW}source $shell_config${NC}"
    echo -e "  • Then: ${YELLOW}hash -r${NC} (clears command cache)"
    echo -e "  • Then: ${YELLOW}$COMMAND_ALIAS${NC}"
    echo ""
    
    if [ "$os" = "windows" ]; then
        echo -e "${BLUE}Option C: IDE/Editor Restart${NC}"
        echo -e "  • If using VS Code or other IDE:"
        echo -e "    1. Save all files"
        echo -e "  • 2. Close the terminal panel"
        echo -e "  • 3. Open a new terminal panel"
        echo -e "  • 4. Type: ${YELLOW}$COMMAND_ALIAS${NC}"
        echo ""
        
        echo -e "${BLUE}Option D: VS Code Specific${NC}"
        echo -e "  • Press ${YELLOW}Ctrl+Shift+P${NC}"
        echo -e "  • Type: ${YELLOW}Terminal: Kill Active Terminal Instance${NC}"
        echo -e "  • Open new terminal and try: ${YELLOW}$COMMAND_ALIAS${NC}"
        echo ""
    fi
    
    echo -e "${MAGENTA}${BOLD}Why restart is needed:${NC}"
    echo -e "  • Shell aliases are loaded when the shell starts"
    echo -e "  • The current session has cached the command list"
    echo -e "  • Reloading clears this cache and reads new aliases"
    echo ""
    
    # Offer to test the command
    if ask_yes_no "Would you like to test the '$COMMAND_ALIAS' command now?"; then
        echo ""
        print_info "Testing: $COMMAND_ALIAS"
        echo -e "${CYAN}${NC}"
        
        # Try to run the command with error handling
        if eval "$COMMAND_ALIAS --help" 2>&1 || eval "$COMMAND_ALIAS -h" 2>&1 || eval "$COMMAND_ALIAS" 2>&1; then
            echo ""
            print_success "'$COMMAND_ALIAS' command is working!"
        else
            echo ""
            print_warning "Command test failed - you may need to restart your terminal"
            print_info "After restarting, try: $COMMAND_ALIAS"
        fi
        echo -e "${CYAN}${NC}"
    fi
}

# ============================================================
# MAIN SETUP FLOW
# ============================================================

main() {
    # Print header
    print_header
    
    echo -e "${CYAN}This wizard will:${NC}"
    echo -e "  • Detect and validate Python installation"
    echo -e "  • Check Git configuration"
    echo -e "  • Validate project files"
    echo -e "  • Configure shell aliases"
    echo ""
    
    if ! ask_yes_no "Ready to begin?"; then
        echo ""
        echo -e "${YELLOW}Setup cancelled by user.${NC}"
        exit 0
    fi
    
    # Run validations
    validate_python || exit 1
    validate_git || true  # Git is optional
    validate_files || exit 1
    validate_permissions || exit 1

    # Install dependencies
    install_dependencies

    # Configure alias
    configure_shell_alias
    
    # Clear terminal cache
    clear_terminal_cache
    
    # Print completion message
    print_completion_message
    
    # Offer to reload config
    reload_shell_config
    
    # Final message
    echo -e "${GREEN}${BOLD}Setup completed successfully!${NC}\n"

}

# ============================================================
# ERROR HANDLING
# ============================================================

# Trap errors
trap 'echo -e "\n${RED}${BOLD}Setup failed. Please check the errors above.${NC}\n"; exit 1' ERR

# Trap Ctrl+C
trap 'echo -e "\n\n${YELLOW}Setup cancelled by user.${NC}\n"; exit 130' INT

# ============================================================
# ENTRY POINT
# ============================================================

main "$@"

exit 0