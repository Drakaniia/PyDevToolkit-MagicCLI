"""
Base menu class and menu item definitions
"""

from abc import ABC, abstractmethod
from typing import List, Callable, Any
from .renderer import MenuRenderer
from .navigation import MenuNavigation


class MenuItem:
    """Represents a single menu item"""

    def __init__(self, label: str, action: Callable[[], Any]):
        self.label: str = label
        self.action: Callable[[], Any] = action

    def __repr__(self) -> str:
        return f"MenuItem(label='{self.label}')"


class Menu(ABC):
    """
    Abstract base class for all menus with responsive viewport adaptation

    Features:
    - Automatic terminal size detection
    - Smooth scrolling for small viewports
    - Optimized redraw for large menus
    - Arrow key navigation with proper cursor positioning
    """

    def __init__(self, title: str):
        self.title: str = title
        self.items: List[MenuItem] = []
        self._items_initialized: bool = False
        self._renderer: MenuRenderer = MenuRenderer(title)
        self._navigation: MenuNavigation = MenuNavigation()
        self.setup_items()
        self._items_initialized = True

    @abstractmethod
    def setup_items(self) -> None:
        """
        Setup menu items - must be implemented by subclasses

        This method should populate the self.items list with MenuItem objects.
        It is called once during initialization of the menu.
        """
        pass

    def display(
        self,
        selected_idx: int = 0,
        initial: bool = True,
        force_full_redraw: bool = False,
    ) -> None:
        """
        Display menu using renderer

        Args:
            selected_idx: Index of currently selected menu item (1-based)
            initial: Whether this is the initial display
            force_full_redraw: Whether to force a full screen redraw
        """
        self._renderer.display(self.items, selected_idx, initial, force_full_redraw)

    def get_choice_with_arrows(self) -> int:
        """
        Get user choice using arrow keys (if available)

        Returns:
            int: Index of the selected menu item (1-based)
        """
        return self._navigation.get_choice_with_arrows(self.items, self._renderer)

    def run(self) -> None:
        """
        Run menu loop until user exits

        This method handles the main menu display and user interaction loop.
        It will continue until a menu item returns "exit".
        """
        while True:
            try:
                choice = self.get_choice_with_arrows()

                # Clear screen only after a selection is made, not during
                # navigation
                result = self.items[choice - 1].action()
                if result == "exit":
                    break
            except KeyboardInterrupt:
                # Handle Ctrl+C globally to return to main menu instead of
                # crashing
                print("\n\nOperation cancelled by user.")
                self.clear_screen()
                break

    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen using platform-appropriate method"""
        MenuRenderer.clear_screen()
