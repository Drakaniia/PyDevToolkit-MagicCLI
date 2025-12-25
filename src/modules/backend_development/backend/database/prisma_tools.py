"""
Prisma Database Tools Module
Provides tools for working with Prisma ORM
"""
from core.menu import Menu, MenuItem
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))


class PrismaTools(Menu):
    """Prisma Database Tools Menu with Prisma ORM operations"""

    def __init__(self):
        super().__init__("Prisma Database Tools")

    def setup_items(self):
        """Setup Prisma tools menu items"""
        if self.items:
            return

        self.items = [
            MenuItem("Test Database Connection", self._test_database_connection),
            MenuItem("Pull Database Schema", self._pull_database_schema),
            MenuItem("Launch Prisma Studio", self._launch_prisma_studio),
            MenuItem("Push Schema to Database", self._push_schema_to_database),
            MenuItem("Generate Prisma Client", self._generate_prisma_client),
            MenuItem("Back to Database Management", self._back_to_db)
        ]

    def _run_prisma_command(self, command, description):
        """Execute a Prisma command using npx"""
        try:
            print(f"\n{description}...")

            # Check if package.json exists to determine if npx is needed
            package_json_path = Path.cwd() / "package.json"
            if package_json_path.exists():
                cmd = ["npx", "prisma"] + command.split()
            else:
                cmd = ["prisma"] + command.split()

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("Command executed successfully!")
                if result.stdout:
                    print("\nOutput:")
                    print(result.stdout)
                return True
            else:
                print("Command failed!")
                if result.stderr:
                    print("\nError:")
                    print(result.stderr)
                return False
        except FileNotFoundError:
            print("Prisma CLI not found. Please install Prisma in your project:")
            print("   npm install prisma @prisma/client")
            print("   Or install globally: npm install -g prisma")
            input("\nPress Enter to continue...")
            return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            input("\nPress Enter to continue...")
            return False

    def _test_database_connection(self):
        """Test if the database connection works using Prisma"""
        self.clear_screen()
        print("=" * 60)
        print("  Test Database Connection")
        print("=" * 60)
        print("\nThis will test the database connection using Prisma.")
        print("Make sure you have a schema.prisma file in your project.")

        success = self._run_prisma_command(
            "db pull --force",
            "Testing database connection with 'prisma db pull'"
        )

        if success:
            print("\nDatabase connection test successful!")
        else:
            print("\nDatabase connection test failed!")

        input("\nPress Enter to continue...")
        return None

    def _pull_database_schema(self):
        """Pull database schema using Prisma"""
        self.clear_screen()
        print("=" * 60)
        print("  Pull Database Schema")
        print("=" * 60)
        print("\nThis will pull the database schema to update your Prisma schema file.")

        success = self._run_prisma_command(
            "db pull",
            "Pulling database schema with 'prisma db pull'"
        )

        if success:
            print("\nSchema pulled successfully!")
        else:
            print("\nSchema pull failed!")

        input("\nPress Enter to continue...")
        return None

    def _launch_prisma_studio(self):
        """Launch Prisma Studio to inspect the database"""
        self.clear_screen()
        print("=" * 60)
        print("  Launch Prisma Studio")
        print("=" * 60)
        print("\nThis will launch Prisma Studio for database inspection.")
        print("Prisma Studio provides a GUI to browse and edit your database.")

        try:
            print("\nLaunching Prisma Studio...")

            # Check if package.json exists to determine if npx is needed
            package_json_path = Path.cwd() / "package.json"
            if package_json_path.exists():
                cmd = ["npx", "prisma", "studio"]
            else:
                cmd = ["prisma", "studio"]

            # Start Prisma Studio in the background
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print("Prisma Studio launched successfully!")
            print("   It should be available at http://localhost:5555")
            print("\nNote: Prisma Studio is now running in the background.")
            print("Press Enter to continue (Studio will keep running)...")
            input()

            # Note: We're not terminating the process here since the user may want to use Studio
            # In a real implementation, you might want to handle process
            # termination
        except FileNotFoundError:
            print("Prisma CLI not found. Please install Prisma in your project:")
            print("   npm install prisma @prisma/client")
            print("   Or install globally: npm install -g prisma")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        input("\nPress Enter to continue...")
        return None

    def _push_schema_to_database(self):
        """Push schema to database using Prisma"""
        self.clear_screen()
        print("=" * 60)
        print("  Push Schema to Database")
        print("=" * 60)
        print("\nThis will push your Prisma schema to the database.")
        print("Warning: This will modify your database schema!")

        confirm = input(
            "\nDo you want to continue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Operation cancelled.")
            input("\nPress Enter to continue...")
            return None

        success = self._run_prisma_command(
            "db push",
            "Pushing schema to database with 'prisma db push'"
        )

        if success:
            print("\nSchema pushed to database successfully!")
        else:
            print("\nSchema push failed!")

        input("\nPress Enter to continue...")
        return None

    def _generate_prisma_client(self):
        """Generate Prisma Client"""
        self.clear_screen()
        print("=" * 60)
        print("  Generate Prisma Client")
        print("=" * 60)
        print("\nThis will generate the Prisma Client based on your schema.")

        success = self._run_prisma_command(
            "generate",
            "Generating Prisma Client with 'prisma generate'"
        )

        if success:
            print("\nPrisma Client generated successfully!")
        else:
            print("\nPrisma Client generation failed!")

        input("\nPress Enter to continue...")
        return None

    def _back_to_db(self):
        """Return to database management menu"""
        return "exit"


def main():
    """Test function to run the Prisma tools menu"""
    menu = PrismaTools()
    menu.run()


if __name__ == "__main__":
    main()
