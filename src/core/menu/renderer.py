"""
Menu rendering and display utilities
"""
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Any
class TerminalInfo:
    """Handle terminal size and viewport information"""

    _cached_size: Optional[Tuple[int, int]] = None
    _last_check_time: float = 0
    _check_interval: float = 0.5  # Only check size every 0.5 seconds to reduce overhead

    @classmethod
    def get_size(cls) -> Tuple[int, int]:
        """Get current terminal size (columns, lines) with caching and rate limiting"""
        import time
        current_time = time.time()

        # Only update cache if enough time has passed or cache is empty
        if cls._cached_size is None or (current_time - cls._last_check_time) > cls._check_interval:
            try:
                size = shutil.get_terminal_size(fallback=(80, 24))
                cls._cached_size = (size.columns, size.lines)
                cls._last_check_time = current_time
            except Exception:
                if cls._cached_size is None:  # Only use fallback if no previous value
                    cls._cached_size = (80, 24)
                cls._last_check_time = current_time

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
        cls._last_check_time = 0
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
        # Only invalidate cache if it's initial display or forced redraw to reduce overhead
        if initial or force_full_redraw:
            TerminalInfo.invalidate_cache()

        cols, lines = TerminalInfo.get_size()
        available_lines = TerminalInfo.get_available_lines()
        is_small = TerminalInfo.is_small_viewport()

        # Adjust scroll offset to keep selected item visible
        old_scroll_offset = self._scroll_offset
        if len(items) > available_lines:
            # Calculate scroll position
            if selected_idx < self._scroll_offset:
                self._scroll_offset = selected_idx
            elif selected_idx >= self._scroll_offset + available_lines:
                self._scroll_offset = selected_idx - available_lines + 1
        else:
            self._scroll_offset = 0

        # Do a full redraw when scrolling offset changes to properly update scroll indicators
        if initial or force_full_redraw or self._scroll_offset != old_scroll_offset:
            self._display_full(items, selected_idx, cols, lines, available_lines, is_small)
        else:
            # Only update the changed items for smooth navigation
            # but also update scroll indicators if they've changed
            self._update_visible_items_and_indicators(items, selected_idx, available_lines, cols)

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

        print(f"  [DIR] Current Directory: {current_dir}")
        print("=" * sep_width)

        # Calculate visible range
        visible_start = self._scroll_offset
        visible_end = min(visible_start + available_lines, len(items))

        # Show scroll indicator at top if needed
        if self._scroll_offset > 0:
            scroll_info = f"  ^ {self._scroll_offset} more above..."
            print(scroll_info[:cols-2])

        # Display visible menu items
        for i in range(visible_start, visible_end):
            self._print_item(i, items[i], i == selected_idx, cols)

        # Show scroll indicator at bottom if needed
        if visible_end < len(items):
            remaining = len(items) - visible_end
            scroll_info = f"  v {remaining} more below..."
            print(scroll_info[:cols-2])

        print("=" * sep_width)

        # Footer - adapt instructions based on viewport and capabilities
        if is_small:
            if self._has_arrow_support():
                print("\n  ^/v: Navigate | Enter: Select")
            else:
                print("\n  Type number + Enter")
        else:
            if self._has_arrow_support():
                print("\n  Use ^/v arrow keys to navigate, Enter to select, or type number")
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
        base_line = 6  # Start from line 6 (1-indexed for ANSI escape codes)
        if self._scroll_offset > 0:
            base_line += 1

        # Calculate the full range of lines that need to be updated
        # This includes potential blank lines at the end
        total_visible_lines = min(available_lines, len(items) - visible_start)

        # Prepare content for all potentially visible lines
        lines_to_update = []
        for idx_in_viewport in range(total_visible_lines):
            actual_idx = visible_start + idx_in_viewport

            if actual_idx < len(items):
                # There's an actual item to display at this position
                item = items[actual_idx]
                line_text = f"{actual_idx + 1}. {item.label}"

                # Truncate if too long for terminal
                max_text_width = cols - 6  # Leave space for prefix and padding
                if len(line_text) > max_text_width:
                    line_text = line_text[:max_text_width-3] + "..."

                # Format the line based on selection state
                if actual_idx == selected_idx:
                    full_line = f"  > {line_text}"
                    full_line = full_line.ljust(min(70, cols - 2))
                    formatted_line = f"\033[1;46m{full_line}\033[0m"
                else:
                    full_line = f"    {line_text}"
                    formatted_line = full_line
            else:
                # This line is beyond our items, so it should be blank
                formatted_line = " " * cols  # Fill with spaces to clear

            lines_to_update.append((base_line + idx_in_viewport, formatted_line))

        # Batch update all lines needed to reduce flickering
        for line_num, content in lines_to_update:
            sys.stdout.write(f'\033[{line_num};1H')  # Move cursor to line, column 1
            sys.stdout.write(self.CLEAR_LINE)  # Clear the entire line
            sys.stdout.write(content)  # Write the new content

        sys.stdout.flush()

    def _update_visible_items_and_indicators(self, items: List[Any], selected_idx: int, available_lines: int, cols: int) -> None:
        """
        Update visible menu items and scroll indicators for smooth navigation

        This handles both the menu items and the scroll indicators without flickering
        """
        visible_start = self._scroll_offset
        visible_end = min(visible_start + available_lines, len(items))

        # Calculate cursor positions
        # Header is 5 lines, scroll indicator adds 1 if present
        base_line = 6  # Start from line 6 (1-indexed for ANSI escape codes)

        # Track if we have scroll indicators and their positions
        has_top_indicator = self._scroll_offset > 0
        has_bottom_indicator = visible_end < len(items)

        # Prepare content for all lines that need to be updated
        lines_to_update = []

        # First, handle the top scroll indicator if needed
        if has_top_indicator:
            remaining = self._scroll_offset
            scroll_info = f"  ^ {remaining} more above..."
            scroll_info = scroll_info[:cols-2]  # Truncate if needed
            lines_to_update.append((6, scroll_info))  # Top indicator is at line 6
            # Adjust base line for menu items since we have a top indicator
            actual_base_line = 7
        else:
            actual_base_line = 6

        # Prepare content for all menu items in the visible range
        for idx_in_viewport in range(visible_end - visible_start):
            actual_idx = visible_start + idx_in_viewport
            # There's definitely an item to display at this position
            item = items[actual_idx]
            line_text = f"{actual_idx + 1}. {item.label}"

            # Truncate if too long for terminal
            max_text_width = cols - 6  # Leave space for prefix and padding
            if len(line_text) > max_text_width:
                line_text = line_text[:max_text_width-3] + "..."

            # Format the line based on selection state
            if actual_idx == selected_idx:
                full_line = f"  > {line_text}"
                full_line = full_line.ljust(min(70, cols - 2))
                formatted_line = f"\033[1;46m{full_line}\033[0m"
            else:
                full_line = f"    {line_text}"
                formatted_line = full_line

            actual_line_num = actual_base_line + idx_in_viewport
            lines_to_update.append((actual_line_num, formatted_line))

        # Handle the bottom scroll indicator if needed
        if has_bottom_indicator:
            remaining = len(items) - visible_end
            scroll_info = f"  v {remaining} more below..."
            scroll_info = scroll_info[:cols-2]  # Truncate if needed
            # Calculate where the bottom indicator should go
            bottom_line_num = actual_base_line + (visible_end - visible_start)
            lines_to_update.append((bottom_line_num, scroll_info))

        # Clear any remaining lines that might still show old content
        total_lines_used = (visible_end - visible_start)  # Menu items
        if has_top_indicator:
            total_lines_used += 1  # Top indicator
        if has_bottom_indicator:
            total_lines_used += 1  # Bottom indicator

        # Add blank lines for any remaining space
        remaining_available_lines = available_lines - (visible_end - visible_start)
        if has_top_indicator:
            remaining_available_lines -= 1
        if has_bottom_indicator:
            remaining_available_lines -= 1

        for i in range(remaining_available_lines):
            if has_bottom_indicator:
                # If there's a bottom indicator, blank lines come after it
                blank_line_num = actual_base_line + (visible_end - visible_start) + 1 + i
            else:
                # If no bottom indicator, blank lines come after the menu items
                blank_line_num = actual_base_line + (visible_end - visible_start) + i
            lines_to_update.append((blank_line_num, " " * cols))

        # Batch update all lines needed to reduce flickering
        for line_num, content in lines_to_update:
            sys.stdout.write(f'\033[{line_num};1H')  # Move cursor to line, column 1
            sys.stdout.write(self.CLEAR_LINE)  # Clear the entire line
            sys.stdout.write(content)  # Write the new content

        sys.stdout.flush()

    def _print_item(self, index: int, item: Any, is_selected: bool, cols: int) -> None:
        """Print a single menu item with proper formatting"""
        line_text = f"{index + 1}. {item.label}"

        # Truncate if too long for terminal
        max_text_width = cols - 6  # Leave space for prefix and padding

        if is_selected:
            full_line = f"  > {line_text}"
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
            full_line = f"  > {line_text}"
            full_line = full_line.ljust(min(70, cols - 2))
            # Apply highlight and then reset formatting
            sys.stdout.write(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            # Ensure we reset formatting first, then write content
            sys.stdout.write(f"\033[0m{full_line}")

    def _print_item_to_buffer(self, index: int, item: Any, is_selected: bool, cols: int, buffer: List[str]) -> None:
        """Add item output to buffer instead of writing directly to stdout"""
        line_text = f"{index + 1}. {item.label}"

        max_text_width = cols - 6
        if len(line_text) > max_text_width:
            line_text = line_text[:max_text_width-3] + "..."

        if is_selected:
            full_line = f"  > {line_text}"
            full_line = full_line.ljust(min(70, cols - 2))
            # Apply highlight and then reset formatting
            buffer.append(f"\033[1;46m{full_line}\033[0m")
        else:
            full_line = f"    {line_text}"
            # Ensure we reset formatting first, then write content
            buffer.append(f"\033[0m{full_line}")

    def _calculate_header_info(self, cols: int, lines: int, available_lines: int, is_small: bool) -> List[str]:
        """Calculate header lines to avoid recalculation during updates"""
        # Calculate separator width for terminal size
        sep_width = min(70, cols - 2)
        header_lines = []

        header_lines.append("=" * sep_width + "\n")

        # Truncate title if needed
        title_display = self.title[:cols-4] if len(self.title) > cols-4 else self.title
        header_lines.append(f"  {title_display}\n")

        header_lines.append("=" * sep_width + "\n")

        # Current directory info (truncate for small viewports)
        from pathlib import Path
        current_dir = str(Path.cwd())
        if len(current_dir) > cols - 25:
            # Show last part of path
            current_dir = "..." + current_dir[-(cols-28):]

        header_lines.append(f"  [DIR] Current Directory: {current_dir}\n")
        header_lines.append("=" * sep_width + "\n")

        return header_lines

    def _has_arrow_support(self) -> bool:
        """Check if terminal supports arrow keys"""
        try:
            import tty  # noqa: F401
            import termios  # noqa: F401
            return True
        except ImportError:
            try:
                import msvcrt  # noqa: F401
                return True
            except ImportError:
                return False

    @staticmethod
    def clear_screen() -> None:
        """Clear the terminal screen and invalidate terminal size cache"""
        # Use ANSI escape codes for faster clearing without system call
        sys.stdout.write('\033[2J\033[H')  # Clear screen and move cursor to home
        sys.stdout.flush()
        # Invalidate terminal size cache since window dimensions might change after clear
        TerminalInfo.invalidate_cache()

