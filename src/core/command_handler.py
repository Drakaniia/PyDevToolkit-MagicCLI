"""
Command Handler Module for Python Automation System

This module provides a command handling system that can be integrated
with the menu system to execute various automation tasks.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import os


class Command(ABC):
    """Abstract base class for all commands"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the command with given arguments"""
        pass

    def __str__(self):
        return f"{self.name}: {self.description}"


class CommandRegistry:
    """Registry for managing available commands"""

    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command):
        """Register a command"""
        self._commands[command.name.lower()] = command

    def get(self, name: str) -> Optional[Command]:
        """Get a command by name"""
        return self._commands.get(name.lower())

    def list_commands(self) -> list:
        """List all available commands"""
        return list(self._commands.values())

    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """Execute a command by name"""
        command = self.get(name)
        if not command:
            raise ValueError(f"Command '{name}' not found")
        return command.execute(*args, **kwargs)

    def has_command(self, name: str) -> bool:
        """Check if command exists"""
        return name.lower() in self._commands


class BaseCommandHandler:
    """Base command handler with common functionality"""

    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    def handle_input(self, user_input: str) -> Any:
        """
        Handle user input and execute appropriate command

        Args:
            user_input: Raw user input string

        Returns:
            Result of command execution
        """
        if not user_input.strip():
            return None

        parts = user_input.strip().split()
        command_name = parts[0].lower()
        args = parts[1:]

        if self.registry.has_command(command_name):
            return self.registry.execute_command(command_name, *args)
        else:
            raise ValueError(f"Unknown command: {command_name}")


class CLICommandHandler:
    """Command handler specifically designed for CLI interaction"""

    def __init__(self):
        self.registry = CommandRegistry()
        self._setup_default_commands()

    def _setup_default_commands(self):
        """Setup default commands available in the system"""
        self.registry.register(HelpCommand(self.registry))
        self.registry.register(ExitCommand())
        self.registry.register(ClearCommand())

    def run_interactive(self):
        """Run interactive command loop"""
        print("Python Automation Command Handler")
        print("Type 'help' for available commands, 'exit' to quit")
        print("-" * 50)

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "q"]:
                    result = self.registry.execute_command("exit")
                    if result == "exit":
                        break
                    continue

                result = self.handle_input(user_input)
                if result is not None:
                    print(result)

            except KeyboardInterrupt:
                print("\n\nKeyboardInterrupt received. Type 'exit' to quit.")
            except EOFError:
                print("\n\nEOF received. Exiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def handle_input(self, user_input: str) -> Any:
        """Handle user input and execute appropriate command"""
        if not user_input.strip():
            return None

        parts = user_input.strip().split()
        command_name = parts[0].lower()
        args = parts[1:]

        if self.registry.has_command(command_name):
            return self.registry.execute_command(command_name, *args)
        else:
            return (
                f"Unknown command: {command_name}. Type 'help' for available commands."
            )


class HelpCommand(Command):
    """Command to show help information"""

    def __init__(self, registry: CommandRegistry):
        super().__init__("help", "Show available commands and their usage")
        self.registry = registry

    def execute(self, *args) -> str:
        """Show help information"""
        if args:
            # Show help for specific command
            command_name = args[0].lower()
            command = self.registry.get(command_name)
            if command:
                return f"{command.name}: {command.description}"
            else:
                return f"No help available for command: {command_name}"

        # Show all commands
        commands = self.registry.list_commands()
        if not commands:
            return "No commands available."

        help_text = "Available commands:\n"
        for cmd in commands:
            help_text += f"  {cmd.name}: {cmd.description}\n"
        return help_text.rstrip()


class ExitCommand(Command):
    """Command to exit the application"""

    def __init__(self):
        super().__init__("exit", "Exit the application")

    def execute(self, *args) -> str:
        """Execute exit command"""
        return "exit"


class ClearCommand(Command):
    """Command to clear the screen"""

    def __init__(self):
        super().__init__("clear", "Clear the screen")

    def execute(self, *args) -> str:
        """Execute clear command"""
        os.system("cls" if os.name == "nt" else "clear")
        return ""


# Example usage and testing
if __name__ == "__main__":
    handler = CLICommandHandler()
    handler.run_interactive()
