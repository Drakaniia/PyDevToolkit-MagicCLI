#!/bin/bash

# ============================================================
# PyDevToolkit-MagicCLI Shell Config Backup Restorer
# ============================================================
# This script helps restore shell configuration backups
# created during installation.
# ============================================================

set -e

# ============================================================
# CONFIGURATION
# ============================================================

INSTALL_DIR="$HOME/.magic-cli"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================================
# HELPER FUNCTIONS
# ============================================================

print_header() {
    clear
    echo -e "\n${BLUE}${BOLD}${NC}"
    echo -e "${BLUE}${BOLD}  PyDevToolkit-MagicCLI - Shell Config Backup Restorer   ${NC}"
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

detect_shell() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$FISH_VERSION" ]; then
        echo "fish"
    else
        echo "unknown"
    fi
}

get_shell_config() {
    local shell_type=$(detect_shell)

    case "$shell_type" in
        bash)
            # Prefer bash_profile for login shells, fallback to bashrc
            if [ -f "$HOME/.bash_profile" ]; then
                echo "$HOME/.bash_profile"
            elif [ -f "$HOME/.bash_login" ]; then
                echo "$HOME/.bash_login"
            else
                echo "$HOME/.bashrc"
            fi
            ;;
        zsh)
            echo "$HOME/.zshrc"
            ;;
        fish)
            echo "$HOME/.config/fish/config.fish"
            ;;
        *)
            # Fallback to bashrc
            echo "$HOME/.bashrc"
            ;;
    esac
}

# ============================================================
# RESTORATION FUNCTION
# ============================================================

restore_backup() {
    print_section "Shell Config Backup Restoration"

    local shell_config=$(get_shell_config)
    local shell_type=$(detect_shell)

    print_info "Detected shell: $shell_type"
    print_info "Shell config: $shell_config"
    echo ""

    # Find available backups
    local backups=()
    while IFS= read -r -d '' file; do
        backups+=("$file")
    done < <(find "$HOME" -maxdepth 1 -name "$(basename "$shell_config").backup.*" -type f -print0 2>/dev/null | sort -rz)

    if [ ${#backups[@]} -eq 0 ]; then
        print_error "No backups found for $shell_config"
        echo ""
        print_info "Expected backup format: ${shell_config}.backup.YYYYMMDD_HHMMSS"
        return 1
    fi

    print_success "Found ${#backups[@]} backup(s):"
    echo ""
    for i in "${!backups[@]}"; do
        local backup_file="${backups[$i]}"
        local backup_date=$(basename "$backup_file" | grep -oP '\d{8}_\d{6}' || echo "Unknown")
        local backup_size=$(du -h "$backup_file" | cut -f1)
        echo "  $((i+1)). $(basename "$backup_file")"
        echo "     Date: $backup_date | Size: $backup_size"
    done

    echo ""
    echo -e "${YELLOW}Which backup would you like to restore? [1-${#backups[@]}] (or 'c' to cancel):${NC} "
    read -r choice

    if [ "$choice" = "c" ] || [ "$choice" = "C" ]; then
        print_info "Restoration cancelled"
        return 0
    fi

    if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#backups[@]} ]; then
        print_error "Invalid choice"
        return 1
    fi

    local selected_backup="${backups[$((choice-1))]}"

    echo ""
    print_warning "You are about to restore: $(basename "$selected_backup")"
    print_warning "This will overwrite your current shell configuration"
    echo ""

    # Show diff preview
    if command -v diff &> /dev/null; then
        print_info "Preview of changes:"
        echo ""
        if diff -u "$shell_config" "$selected_backup" | head -20; then
            print_info "No differences found"
        else
            echo ""
            print_info "(Showing first 20 lines of differences)"
        fi
        echo ""
    fi

    echo -e "${YELLOW}Continue with restoration? [Y/n]:${NC} "
    read -r confirm

    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        print_info "Restoration cancelled"
        return 0
    fi

    # Create a backup of current config before restoring
    if [ -f "$shell_config" ]; then
        local current_backup="${shell_config}.before_restore.$(date +%Y%m%d_%H%M%S)"
        cp "$shell_config" "$current_backup"
        print_success "Current config backed up to: $(basename "$current_backup")"
    fi

    # Restore selected backup
    cp "$selected_backup" "$shell_config"

    print_success "Restored backup: $(basename "$selected_backup")"
    echo ""
    print_info "Next steps:"
    print_info "  1. Restart your terminal completely"
    print_info "  2. Or run: source $shell_config"
    echo ""

    # Ask if user wants to remove the restored backup
    echo -e "${YELLOW}Remove the restored backup file? [y/N]:${NC} "
    read -r remove_backup

    if [[ "$remove_backup" =~ ^[Yy]$ ]]; then
        rm "$selected_backup"
        print_success "Removed backup: $(basename "$selected_backup")"
    fi

    return 0
}

# ============================================================
# LIST BACKUPS FUNCTION
# ============================================================

list_backups() {
    print_section "Available Backups"

    local shell_config=$(get_shell_config)

    local backups=()
    while IFS= read -r -d '' file; do
        backups+=("$file")
    done < <(find "$HOME" -maxdepth 1 -name "$(basename "$shell_config").backup.*" -type f -print0 2>/dev/null | sort -rz)

    if [ ${#backups[@]} -eq 0 ]; then
        print_warning "No backups found"
        return 0
    fi

    print_success "Found ${#backups[@]} backup(s):"
    echo ""
    for backup in "${backups[@]}"; do
        local backup_date=$(basename "$backup" | grep -oP '\d{8}_\d{6}' || echo "Unknown")
        local backup_size=$(du -h "$backup" | cut -f1)
        local backup_perms=$(ls -l "$backup" | awk '{print $1}')
        echo "  • $(basename "$backup")"
        echo "    Date: $backup_date | Size: $backup_size | Permissions: $backup_perms"
    done

    echo ""
    print_info "Run this script again to restore a backup"
}

# ============================================================
# MAIN MENU
# ============================================================

main_menu() {
    print_header

    echo -e "${CYAN}Select an option:${NC}"
    echo ""
    echo "  1. Restore a backup"
    echo "  2. List all backups"
    echo "  3. Exit"
    echo ""

    echo -e "${YELLOW}Enter your choice [1-3]:${NC} "
    read -r choice

    case "$choice" in
        1)
            restore_backup
            ;;
        2)
            list_backups
            ;;
        3)
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# ============================================================
# MAIN EXECUTION
# ============================================================

# Check if a specific action was requested via command line
case "${1:-}" in
    --list|-l)
        print_header
        list_backups
        ;;
    --restore|-r)
        print_header
        restore_backup
        ;;
    --help|-h)
        print_header
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  --list, -l     List all available backups"
        echo "  --restore, -r  Restore a backup (interactive)"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Without options, this script shows an interactive menu."
        ;;
    *)
        main_menu
        ;;
esac