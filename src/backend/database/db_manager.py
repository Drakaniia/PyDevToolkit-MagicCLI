"""
Database Management Module
PostgreSQL Quick Commands and Prisma Tools
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from menu import Menu, MenuItem


class DatabaseManager(Menu):
    """Database Management Menu with PostgreSQL and Prisma tools"""

    def __init__(self):
        super().__init__("🗄️ Database Management")

    def setup_items(self):
        """Setup database management menu items"""
        if self.items:
            return

        self.items = [
            MenuItem("🐘 PostgreSQL Quick Commands", self._run_postgres_commands),
            MenuItem("🔷 Prisma Database Tools", self._run_prisma_tools),
            MenuItem("🔙 Back to Backend Dev", self._back_to_backend)
        ]

    def _run_postgres_commands(self):
        """Run PostgreSQL quick commands menu"""
        from backend.database.postgres_commands import PostgresCommands
        postgres_commands = PostgresCommands()
        postgres_commands.run()
        return None

    def _run_prisma_tools(self):
        """Run Prisma database tools menu"""
        from backend.database.prisma_tools import PrismaTools
        prisma_tools = PrismaTools()
        prisma_tools.run()
        return None

    def _back_to_backend(self):
        """Return to backend development menu"""
        return "exit"