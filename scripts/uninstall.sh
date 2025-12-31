#!/bin/bash

# ============================================================
# PyDevToolkit-MagicCLI Global Uninstaller
# ============================================================
# This script completely removes PyDevToolkit-MagicCLI
# installed via the automated bash installer.
# ============================================================

set -e  # Exit on error

# ============================================================
# CONFIGURATION
# ============================================================

PACKAGE_NAME="magic-cli"
INSTALL_DIR="$HOME/.magic-cli"

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
    echo -e "${BLUE}${BOLD}  PyDevToolkit-MagicCLI Global Uninstaller                ${NC}"
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

# ============================================================
# SYSTEM DETECTION
# ============================================================

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

# ============================================================
# PYTHON DETECTION
# ============================================================

find_python_commands() {
    local commands=("python3" "python" "py")
    local found_commands=()

    for cmd in "${commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            # Check if it's Python 3
            local version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)

            if [ "$major" = "3" ]; then
                found_commands+=("$cmd")
            fi
        fi
    done

    echo "${found_commands[@]}"
}

check_package_installed() {
    local python_cmd="$1"
    local package_name="$2"

    if $python_cmd -m pip show "$package_name" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

uninstall_package() {
    local python_cmd="$1"
    local package_name="$2"

    print_info "Uninstalling $package_name using $python_cmd..."

    if $python_cmd -m pip uninstall --yes "$package_name" 2>/dev/null; then
        print_success "Successfully uninstalled $package_name"
        return 0
    else
        print_error "Failed to uninstall $package_name using $python_cmd"
        return 1
    fi
}

clean_pip_cache() {
    print_info "Cleaning pip cache..."

    # Try to clean cache for all found Python commands
    local python_cmds=($(find_python_commands))
    local cache_cleaned=false

    for cmd in "${python_cmds[@]}"; do
        if $cmd -m pip cache purge &> /dev/null; then
            print_success "Cleaned pip cache for $cmd"
            cache_cleaned=true
        fi
    done

    if [ "$cache_cleaned" = false ]; then
        print_warning "Could not clean pip cache (this is usually not a problem)"
    fi
}

# ============================================================
# MAIN UNINSTALLATION LOGIC
# ============================================================

main() {
    print_header

    echo -e "${CYAN}This uninstaller will:${NC}"
    echo -e "  • Remove the installation directory ($INSTALL_DIR)"
    echo -e "  • Remove PyDevToolkit-MagicCLI from PATH"
    echo -e "  • Clean up shell configuration"
    echo -e "  • Optionally uninstall Python packages"
    echo ""

    if ! ask_yes_no "Continue with uninstallation?"; then
        echo ""
        echo -e "${YELLOW}Uninstallation cancelled by user.${NC}"
        exit 0
    fi

    print_section "Checking Installation"

    local found_installation=false

    if [ -d "$INSTALL_DIR" ]; then
        found_installation=true
        print_success "Found installation directory: $INSTALL_DIR"
    else
        print_warning "Installation directory not found: $INSTALL_DIR"
    fi

    # Check if magic command exists
    if command -v magic &> /dev/null; then
        print_success "Found 'magic' command in PATH"
    else
        print_info "'magic' command not found in current PATH"
    fi

    if [ "$found_installation" = false ]; then
        print_warning "No installation found to remove"
        if ask_yes_no "Continue with Python package cleanup anyway?"; then
            print_info "Proceeding with Python package cleanup..."
        else
            echo -e "${YELLOW}Uninstallation cancelled.${NC}"
            exit 0
        fi
    fi

    print_section "Removing Installation Directory"

    if [ -d "$INSTALL_DIR" ]; then
        if rm -rf "$INSTALL_DIR" 2>/dev/null; then
            print_success "Removed installation directory: $INSTALL_DIR"
        else
            print_error "Failed to remove installation directory: $INSTALL_DIR"
            print_info "You may need to run this script with elevated privileges"
        fi
    fi

    print_section "Cleaning Shell Configuration"

    local shell_config=$(get_shell_config)
    local cleaned_config=false

    if [ -f "$shell_config" ]; then
        # Create backup
        cp "$shell_config" "${shell_config}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

        # Remove PyDevToolkit-MagicCLI entries
        sed -i '/# PyDevToolkit-MagicCLI/,+3d' "$shell_config" 2>/dev/null || true

        if [ -f "${shell_config}.backup.$(date +%Y%m%d_%H%M%S)" ]; then
            print_success "Created backup: ${shell_config}.backup.$(date +%Y%m%d_%H%M%S)"
        fi

        print_success "Cleaned shell configuration: $shell_config"
        cleaned_config=true
    else
        print_info "Shell config file not found: $shell_config"
    fi

    print_section "Python Package Cleanup"

    local python_cmds=($(find_python_commands))

    if [ ${#python_cmds[@]} -gt 0 ]; then
        print_info "Found Python installations: ${python_cmds[*]}"

        local package_found=false
        for cmd in "${python_cmds[@]}"; do
            if check_package_installed "$cmd" "$PACKAGE_NAME"; then
                package_found=true
                print_info "Found package installed with $cmd"

                if ask_yes_no "Uninstall Python package from $cmd?"; then
                    if uninstall_package "$cmd" "$PACKAGE_NAME"; then
                        print_success "Uninstalled package from $cmd"
                    fi
                fi
            fi
        done

        if [ "$package_found" = false ]; then
            print_info "No Python packages found to uninstall"
        fi

        # Clean pip cache
        clean_pip_cache
    else
        print_info "No Python installations found"
    fi

    print_section "Verification"

    # Check if everything is cleaned up
    if [ ! -d "$INSTALL_DIR" ]; then
        print_success "Installation directory removed"
    else
        print_warning "Installation directory still exists: $INSTALL_DIR"
    fi

    if ! command -v magic &> /dev/null; then
        print_success "'magic' command removed from PATH"
    else
        print_warning "'magic' command still available (restart terminal to refresh PATH)"
    fi

    print_section "Uninstallation Complete"

    echo -e "${GREEN}${BOLD}PyDevToolkit-MagicCLI has been uninstalled!${NC}"
    echo ""
    echo -e "${CYAN}What was removed:${NC}"
    echo -e "  • Installation directory: $INSTALL_DIR"
    echo -e "  • Shell configuration entries"
    echo -e "  • Python packages (if selected)"
    echo -e "  • Pip cache cleaned"
    echo ""

    if [ "$cleaned_config" = true ]; then
        echo -e "${YELLOW}Note:${NC}"
        echo -e "  • Restart your terminal for PATH changes to take effect"
        echo -e "  • The 'magic' command will no longer be available"
        echo ""
    fi

    echo -e "${CYAN}Reinstall anytime with:${NC}"
    echo -e "  ${GREEN}curl -fsSL https://raw.githubusercontent.com/Drakaniia/PyDevToolkit-MagicCLI/main/install.sh | bash${NC}"
    echo ""

    echo -e "${GREEN}Thank you for using PyDevToolkit-MagicCLI!${NC}"
}

# ============================================================
# ERROR HANDLING
# ============================================================

# Trap errors
trap 'echo -e "\n${RED}${BOLD}Uninstallation failed. Please check the errors above.${NC}\n"; exit 1' ERR

# Trap Ctrl+C
trap 'echo -e "\n\n${YELLOW}Uninstallation cancelled by user.${NC}\n"; exit 130' INT

# ============================================================
# ENTRY POINT
# ============================================================

main "$@"