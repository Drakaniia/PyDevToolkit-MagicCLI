"""
PostgreSQL Quick Commands Module
Provides commonly used PostgreSQL commands for quick execution
"""
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.menu import Menu, MenuItem


class PostgresCommands(Menu):
    """PostgreSQL Quick Commands Menu with common PostgreSQL operations"""

    def __init__(self):
        super().__init__("PostgreSQL Quick Commands")

    def setup_items(self):
        """Setup PostgreSQL quick commands menu items"""
        if self.items:
            return

        self.items = [
            MenuItem("Login to PostgreSQL (psql -U postgres)", self._login_with_psql),
            MenuItem("Back to Database Management", self._back_to_db)
        ]

    def _login_with_psql(self):
        """Run psql -U postgres command to login to PostgreSQL"""
        self.clear_screen()
        print("=" * 60)
        print("  Login to PostgreSQL (psql -U postgres)")
        print("=" * 60)

        # Show quick commands reference
        print("\nPostgreSQL Quick Commands Reference (for use in psql session):")
        print("-" * 60)
        print("  Create Database: CREATE DATABASE your_database_name;")
        print("  Drop Database: DROP DATABASE your_database_name;")
        print("  List Databases: \\l")
        print("  Connect to Database: \\c your_database_name")
        print("  Disconnect: \\c postgres")  # Disconnect by connecting to default db
        print("  List Tables: \\dt")
        print("  List All Objects: \\da")
        print("  Create User: CREATE USER your_username WITH PASSWORD 'your_password';")
        print("  Drop User: DROP USER your_username;")
        print("  Grant Privileges: GRANT ALL PRIVILEGES ON DATABASE db_name TO username;")
        print("  Revoke Privileges: REVOKE ALL PRIVILEGES ON DATABASE db_name FROM username;")
        print("  List Users/Roles: \\du")
        print("  Describe Table: \\d table_name")
        print("  Describe All Tables: \\dt+")
        print("  List Schemas: \\dn")
        print("  Create Schema: CREATE SCHEMA schema_name;")
        print("  List Extensions: \\dx")
        print("  Install Extension: CREATE EXTENSION extension_name;")
        print("  Show Current DB: \\conninfo")
        print("  Execute File: \\i file_path")
        print("  Save Output: \\o file_path")
        print("  Cancel Query: \\cancel")
        print("  Exit PostgreSQL: \\q")
        print("-" * 60)

        print("\nWhen using psql, note that:")
        print("  - Commands starting with \\ are meta commands")
        print("  - SQL commands must end with ;")
        print("  - Use \\? for help with psql commands")
        print("  - Use \\h for help with SQL commands")

        input("\nPress Enter to start psql session...")

        try:
            # Run psql command with postgres user
            cmd = ["psql", "-U", "postgres"]
            subprocess.run(cmd)
        except FileNotFoundError:
            print("\nError: psql command not found. Please ensure PostgreSQL is installed and added to your PATH.")
            input("\nPress Enter to return to menu...")
            return None
        except Exception as e:
            print(f"\nError running psql: {str(e)}")
            input("\nPress Enter to return to menu...")
            return None

        print("\n" + "=" * 60)
        print("  PostgreSQL session ended")
        print("=" * 60)
        print("\nWould you like to:")
        print("1. Return to PostgreSQL menu")
        print("2. Exit to database management")

        while True:
            choice = input("\nEnter your choice (1-2): ").strip()
            if choice == "1":
                return None  # Return to menu normally
            elif choice == "2":
                return "exit"
            else:
                print("Invalid choice. Please enter 1 or 2.")

    def _back_to_db(self):
        """Return to database management menu"""
        return "exit"


def main():
    """Test function to run the PostgreSQL quick commands menu"""
    menu = PostgresCommands()
    menu.run()


if __name__ == "__main__":
    main()