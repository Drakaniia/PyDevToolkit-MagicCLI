"""
Menu rendering and display utilities
"""
import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Any


class TerminalInfo:
    """Handle terminal size and viewport information"""

    _cached_size: Optional[Tuple[int, int]] = None

    @classmethod
    def get_size(cls) -> Tuple[int, int]:
        """Get current terminal size (columns, lines) with caching"""
        if cls._cached_size is not None:
            return cls._cached_size

        try:
            size = shutil.get_terminal_size(fallback=(80, 24))
            cls._cached_size = (size.columns, size.lines)
            return cls._cached_size
        except Exception:
            cls._cached_size = (80, 24)
            return cls._cached_size

    @classmethod
    def is_small_viewport(cls) -> bool:
        """Check if terminal viewport is small"""
        cols, lines = cls.get_size()
        return lines < 20 or cols < 70

    @classmethod
    def get_available_lines(cls) -> int:
        """Get number of lines available for menu items"""
        _, lines = cls.get_size()
        # Reserve space for header (5) + footer (3) + padding
        return max(5, lines - 8)

    @classmethod
    def invalidate_cache(cls) -> None:
        """Invalidate the cached terminal size"""
        cls._cached_size = None


class MenuRenderer:
    """Handles menu display and rendering logic"""
    
    # ANSI escape codes for cursor control
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    CLEAR_SCREEN = '\033[2J\033[H'
    CLEAR_LINE = '\033[2K'
    MOVE_UP = '\033[1A'
    
    def __init__(self, title: str):
        self.title: str = title
        self._scroll_offset: int = 0
    
    def display(self, items: List[Any], selected_idx: int = 0, initial: bool = True,
                force_full_redraw: bool = False) -> None:
        """
        Display the menu with responsive viewport handling

        Args:
            items: List of menu items to display
            selected_idx: Currently selected item index
            initial: Whether this is the initial display
            force_full_redraw: Force complete screen refresh
        """
        cols, lines = TerminalInfo.get_size()
        available_lines = TerminalInfo.get_available_lines()
        is_small = TerminalInfo.is_small_viewport()
        
        # Adjust scroll offset to keep selected item visible
        if len(items) > available_lines:
            # Calculate scroll position
            if selected_idx < self._scroll_offset:
                self._scroll_offset = selected_idx
            elif selected_idx >= self._scroll_offset + available_lines:
                self._scroll_offset = selected_idx - available_lines + 1
        else:
            self._scroll_offset = 0
        
        if initial or force_full_redraw:
            self._display_full(items, selected_idx, cols, lines, available_lines, is_small)
        else:
            # Only update the changed items for smooth navigation
            self._update_visible_items(items, selected_idx, available_lines)
    
    def _display_full(self, items: List[Any], selected_idx: int, cols: int, lines: int,
                      available_lines: int, is_small: bool) -> None:
        """Full screen refresh with responsive layout"""
        self.clear_screen()
        
        # Adjust separator width for terminal size
        sep_width = min(70, cols - 2)
        
        # Header
        print("=" * sep_width)
        
        # Truncate title if needed
        title_display = self.title[:cols-4] if len(self.title) > cols-4 else self.title
        print(f"  {title_display}")
        
        print("=" * sep_width)
        
        # Current directory info (truncate for small viewports)
        current_dir = str(Path.cwd())
        if len(current_dir) > cols - 25:
            # Show last part of path
            current_dir = "..." + current_dir[-(cols-28):]
        
        print(f"  📍 Current Directory: {current_dir}")
        print("=" * sep_width)
        
        # Calculate visible range
        visible_start = self._scroll_offset
        visible_end = min(visible_start + available_lines, len(items))
        
        # Show scroll indicator at top if needed
        if self._scroll_offset > 0:
            scroll_info = f"  ↑ {self._scroll_offset} more above..."
            print(scroll_info[:cols-2])
        
        # Display visible menu items
        for i in range(visible_start, visible_end):
            self._print_item(i, items[i], i == selected_idx, cols)
        
        # Show scroll indicator at bottom if needed
        if visible_end < len(items):
            remaining = len(items) - visible_end
            scroll_info = f"  ↓ {remaining} more below..."
            print(scroll_info[:cols-2])
        
        print("=" * sep_width)
        
        # Footer - adapt instructions based on viewport and capabilities
        if is_small:
            if self._has_arrow_support():
                print("\n  ↑/↓: Navigate | Enter: Select")
            else:
                print("\n  Type number + Enter")
        else:
            if self._has_arrow_support():
                print("\n  Use ↑/↓ arrow keys to navigate, Enter to select, or type number")
            else:
                print("\n  Type number and press Enter to select")
    
    def _update_visible_items(self, items: List[Any], selected_idx: int, available_lines: int) -> None:
        """
        Update only the visible menu items for smooth navigation

        This is much faster than full redraw and prevents flickering
        """
        visible_start = self._scroll_offset
        visible_end = min(visible_start + available_lines, len(items))
        cols, _ = TerminalInfo.get_size()

        # Calculate cursor position for updates
        # Header is 5 lines, scroll indicator adds 1 if present
        base_line = 5
        if self._scroll_offset > 0:
            base_line += 1

        # Update each visible item individually
        for i in range(visible_start, visible_end):
            line_number = base_line + (i - visible_start)

            # Move cursor to the line
            sys.stdout.write(f'\033[{line_number + 1};1H')
            sys.stdout.write(self.CLEAR_LINE)

            # Redraw the item with proper selection state
            # Reset formatting first, then add content
            sys.stdout.write('\033[0m')  # Reset all formatting
            self._print_item_inline(i, items[i], i == selected_idx, cols)

        sys.stdout.flush()
    
    def _print_item(self, index: int, item: Any, is_selected: bool, cols: int) -> None:
        """Print a single menu item with proper formatting"""
        line_text = f"{index + 1}. {item.label}"
        
        # Truncate if too long for terminal
        max_text_width = cols - 6  # Leave space for prefix and padding
        if len(line_text) > max_text_width:
            line_text = line_text[:max_text_width-3] + "..."
        
        if is_selected:
            full_line = f"  ► {line_text}"
            # Pad to full width for consistent highlight
            full_line = full_line.ljust(min(70, cols - 2))
            print(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            print(full_line)
    
    def _print_item_inline(self, index: int, item: Any, is_selected: bool, cols: int) -> None:
        """Print item inline (without newline) for updates"""
        line_text = f"{index + 1}. {item.label}"

        max_text_width = cols - 6
        if len(line_text) > max_text_width:
            line_text = line_text[:max_text_width-3] + "..."

        if is_selected:
            full_line = f"  ► {line_text}"
            full_line = full_line.ljust(min(70, cols - 2))
            # Apply highlight and then reset formatting
            sys.stdout.write(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            # Ensure we reset formatting first, then write content
            sys.stdout.write(f"\033[0m{full_line}")
    
    def _has_arrow_support(self) -> bool:
        """Check if terminal supports arrow keys"""
        try:
            import tty
            import termios
            return True
        except ImportError:
            try:
                import msvcrt
                return True
            except ImportError:
                return False
    
    @staticmethod
    def clear_screen() -> None:
        """Clear the terminal screen and invalidate terminal size cache"""
        os.system('cls' if os.name == 'nt' else 'clear')
        # Invalidate terminal size cache since window dimensions might change after clear
        TerminalInfo.invalidate_cache()