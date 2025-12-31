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

detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
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
            local version=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)

            if [ "$major" = "3" ]; then
                found_commands+=("$cmd")
            fi
        fi
    done

    echo "${found_commands[@]}"
}

# ============================================================
# PACKAGE DETECTION
# ============================================================

check_package_installed() {
    local python_cmd="$1"
    local package_name="$2"

    if $python_cmd -m pip show "$package_name" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

get_package_location() {
    local python_cmd="$1"
    local package_name="$2"

    $python_cmd -m pip show "$package_name" 2>/dev/null | grep "Location:" | cut -d' ' -f2-
}

# ============================================================
# UNINSTALLATION FUNCTIONS
# ============================================================

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

remove_config_files() {
    print_info "Checking for configuration files..."

    local os=$(detect_os)
    local config_removed=false

    case "$os" in
        linux|macos)
            local config_dirs=(
                "$HOME/.config/magic-cli"
            )
            ;;
        windows)
            local config_dirs=(
                "$APPDATA/pydevtoolkit-magiccli"
                "$APPDATA/magic-cli"
                "$LOCALAPPDATA/pydevtoolkit-magiccli"
            )
            ;;
    esac

    for config_dir in "${config_dirs[@]}"; do
        if [ -d "$config_dir" ]; then
            if ask_yes_no "Remove configuration directory: $config_dir?"; then
                if rm -rf "$config_dir" 2>/dev/null; then
                    print_success "Removed configuration directory: $config_dir"
                    config_removed=true
                else
                    print_warning "Could not remove configuration directory: $config_dir"
                fi
            fi
        fi
    done

    if [ "$config_removed" = false ]; then
        print_info "No configuration directories found"
    fi
}

# ============================================================
# MAIN UNINSTALLATION LOGIC
# ============================================================

main() {
    print_header

    echo -e "${CYAN}This uninstaller will:${NC}"
    echo -e "  • Remove the PyDevToolkit-MagicCLI package"
    echo -e "  • Clean pip cache"
    echo -e "  • Optionally remove configuration files"
    echo ""

    if ! ask_yes_no "Continue with uninstallation?"; then
        echo ""
        echo -e "${YELLOW}Uninstallation cancelled by user.${NC}"
        exit 0
    fi

    print_section "Detecting Python Installations"

    local python_cmds=($(find_python_commands))

    if [ ${#python_cmds[@]} -eq 0 ]; then
        print_error "No Python 3 installations found"
        echo ""
        print_info "Please ensure Python 3 is installed and try again"
        exit 1
    fi

    print_success "Found Python commands: ${python_cmds[*]}"

    print_section "Checking Package Installation"

    local package_found=false
    local installed_locations=()

    for cmd in "${python_cmds[@]}"; do
        if check_package_installed "$cmd" "$PACKAGE_NAME"; then
            package_found=true
            local location=$(get_package_location "$cmd" "$PACKAGE_NAME")
            installed_locations+=("$cmd: $location")
            print_success "Package found with $cmd at: $location"
        fi
    done

    if [ "$package_found" = false ]; then
        print_warning "Package '$PACKAGE_NAME' not found in any Python installation"
        echo ""
        if ask_yes_no "Continue with cleanup anyway?"; then
            print_info "Proceeding with cleanup..."
        else
            echo -e "${YELLOW}Uninstallation cancelled.${NC}"
            exit 0
        fi
    fi

    if [ ${#installed_locations[@]} -gt 0 ]; then
        print_section "Uninstalling Package"

        for cmd in "${python_cmds[@]}"; do
            if check_package_installed "$cmd" "$PACKAGE_NAME"; then
                if uninstall_package "$cmd" "$PACKAGE_NAME"; then
                    # Remove from installed_locations array
                    installed_locations=("${installed_locations[@]/$cmd:*/}")
                fi
            fi
        done

        # Check if any installations remain
        local remaining_installations=()
        for cmd in "${python_cmds[@]}"; do
            if check_package_installed "$cmd" "$PACKAGE_NAME"; then
                remaining_installations+=("$cmd")
            fi
        done

        if [ ${#remaining_installations[@]} -gt 0 ]; then
            print_warning "Package still installed with: ${remaining_installations[*]}"
            print_info "You may need to run this script with elevated privileges or check permissions"
        else
            print_success "Package successfully uninstalled from all Python installations"
        fi
    fi

    print_section "Cleaning Installation Directory"

    if [ -d "$INSTALL_DIR" ]; then
        if rm -rf "$INSTALL_DIR" 2>/dev/null; then
            print_success "Removed installation directory: $INSTALL_DIR"
        else
            print_error "Failed to remove installation directory: $INSTALL_DIR"
            print_info "You may need to run this script with elevated privileges"
        fi
    else
        print_info "Installation directory not found: $INSTALL_DIR"
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