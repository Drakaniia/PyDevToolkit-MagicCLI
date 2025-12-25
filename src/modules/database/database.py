"""
Database Module
Handles database operations, migrations, seeding, and schema comparison
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class DatabaseTools:
    """Handles database management tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def setup_database_config(self) -> None:
        """Help set up database configuration"""
        print("\n" + "="*70)
        print("DATABASE CONFIGURATION SETUP")
        print("="*70)

        print("\nThis tool helps set up database configuration for your project.")

        # Detect if SQLAlchemy is used
        has_sqlalchemy = False
        try:
            import sqlalchemy
            has_sqlalchemy = True
        except ImportError:
            pass

        if has_sqlalchemy:
            print("✓ SQLAlchemy detected in environment")
        else:
            print("⚠ SQLAlchemy not found. Install with: pip install sqlalchemy")

        # Ask for database type
        print("\nSelect database type:")
        print("  1. PostgreSQL")
        print("  2. MySQL")
        print("  3. SQLite")
        print("  4. MongoDB")

        try:
            choice = input("\nEnter choice (1-4) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_postgres_config()
            elif choice == "2":
                self._setup_mysql_config()
            elif choice == "3":
                self._setup_sqlite_config()
            elif choice == "4":
                self._setup_mongodb_config()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_postgres_config(self) -> None:
        """Set up PostgreSQL configuration"""
        print("\nSetting up PostgreSQL Configuration...")

        # Create example config file
        config_content = '''# PostgreSQL Configuration
# Update these values according to your setup

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# Example connection string:
# postgresql://user:password@host:port/database
'''

        config_path = Path("config") / "database_postgresql.env"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"✓ PostgreSQL configuration template created: {config_path}")

    def _setup_mysql_config(self) -> None:
        """Set up MySQL configuration"""
        print("\nSetting up MySQL Configuration...")

        # Create example config file
        config_content = '''# MySQL Configuration
# Update these values according to your setup

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=your_database_name
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# Example connection string:
# mysql+pymysql://user:password@host:port/database
'''

        config_path = Path("config") / "database_mysql.env"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"✓ MySQL configuration template created: {config_path}")

    def _setup_sqlite_config(self) -> None:
        """Set up SQLite configuration"""
        print("\nSetting up SQLite Configuration...")

        # Create example config file
        config_content = '''# SQLite Configuration

# SQLite is file-based, so specify the path
SQLITE_PATH=./data/database.db

# Example connection string:
# sqlite:///./data/database.db

# For in-memory database (not persistent):
# sqlite:///:memory:
'''

        config_path = Path("config") / "database_sqlite.env"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"✓ SQLite configuration template created: {config_path}")

    def _setup_mongodb_config(self) -> None:
        """Set up MongoDB configuration"""
        print("\nSetting up MongoDB Configuration...")

        # Create example config file
        config_content = '''# MongoDB Configuration

# For local MongoDB
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=your_database_name

# For MongoDB Atlas (cloud)
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name

# Example connection string:
# mongodb://host:port/database
'''

        config_path = Path("config") / "database_mongodb.env"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w') as f:
            f.write(config_content)

        print(f"✓ MongoDB configuration template created: {config_path}")

    def run_database_migrations(self) -> None:
        """Run database migrations using Alembic or similar"""
        print("\n" + "="*70)
        print("DATABASE MIGRATIONS")
        print("="*70)

        print("\nThis feature helps manage database schema changes.")
        print("It typically uses Alembic for SQLAlchemy-based projects.")

        # Check if Alembic is available
        try:
            import alembic
            print("✓ Alembic is available")

            print("\nCommon Alembic commands:")
            print("  alembic init alembic")  # Initialize
            print("  alembic revision --autogenerate -m \"message\"")  # Generate migration
            print("  alembic upgrade head")  # Apply migrations
            print("  alembic downgrade -1")  # Revert migration
        except ImportError:
            print("⚠ Alembic is not installed")
            install = input("Install Alembic? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "alembic"], check=True)
                    print("✓ Alembic installed successfully")
                    print("\nRun 'alembic init alembic' to initialize in your project")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Alembic")

        print("\nFor more complex migration management, use the respective tools.")
        input("\nPress Enter to continue...")

    def seed_database(self) -> None:
        """Seed database with test/fake data"""
        print("\n" + "="*70)
        print("DATABASE SEEDING")
        print("="*70)

        print("\nThis feature would populate your database with test/fake data.")
        print("Implementation depends on your specific models and requirements.")

        # Look for potential data seed files
        seed_pattern = list(Path('.').glob('**/seed*'))
        if seed_pattern:
            print("\nPotential seed files found:")
            for seed_file in seed_pattern[:5]:  # Show first 5
                print(f"  - {seed_file}")

        print("\nTypical implementation involves:")
        print("  1. Creating a seeding script")
        print("  2. Defining sample data for each model")
        print("  3. Running the seeding script")

        # Provide example code
        print("\nExample seeding code:")
        print("```python")
        print("# seeds.py")
        print("from your_app.database import SessionLocal")
        print("from your_app.models import User")
        print()
        print("def seed_users():")
        print("    db = SessionLocal()")
        print("    try:")
        print("        # Create sample users")
        print("        user1 = User(name='John Doe', email='john@example.com')")
        print("        user2 = User(name='Jane Smith', email='jane@example.com')")
        print("        db.add(user1)")
        print("        db.add(user2)")
        print("        db.commit()")
        print("        print('Seeded users successfully')")
        print("    finally:")
        print("        db.close()")
        print("```")

        input("\nPress Enter to continue...")

    def compare_database_schemas(self) -> None:
        """Compare database schemas across environments"""
        print("\n" + "="*70)
        print("DATABASE SCHEMA COMPARISON")
        print("="*70)

        print("\nThis feature compares database schemas across different environments.")
        print("For this to work, you need to specify connection details for both databases.")

        print("\nWithout specific database access details, here's how you would typically approach this:")
        print("  1. Connect to source database")
        print("  2. Connect to target database")
        print("  3. Extract schema information from both")
        print("  4. Compare and report differences")

        print("\nCommon tools for schema comparison:")
        print("  - For PostgreSQL: pg_dump and diff tools")
        print("  - For MySQL: mysqldump and diff tools")
        print("  - Using SQLAlchemy reflection to compare models")

        # Provide example code
        print("\nExample schema comparison code:")
        print("```python")
        print("# schema_diff.py")
        print("from sqlalchemy import create_engine, text")
        print("from sqlalchemy.exc import SQLAlchemyError")
        print()
        print("def compare_schemas(source_url, target_url):")
        print("    source_engine = create_engine(source_url)")
        print("    target_engine = create_engine(target_url)")
        print("    ")
        print("    try:")
        print("        # Get list of tables in both databases")
        print("        with source_engine.connect() as conn:")
        print("            source_tables = [row[0] for row in conn.execute(text(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\"))]")
        print("        ")
        print("        with target_engine.connect() as conn:")
        print("            target_tables = [row[0] for row in conn.execute(text(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\"))]")
        print("        ")
        print("        print('Tables only in source:', set(source_tables) - set(target_tables))")
        print("        print('Tables only in target:', set(target_tables) - set(source_tables))")
        print("    except SQLAlchemyError as e:")
        print("        print(f'Error comparing schemas: {e}')")
        print("```")

        input("\nPress Enter to continue...")

    def run_database_backup(self) -> None:
        """Create database backup"""
        print("\n" + "="*70)
        print("DATABASE BACKUP")
        print("="*70)

        print("\nDatabase backup functionality depends on the specific database system.")
        print("Here are common approaches for different databases:")

        print("\nPostgreSQL:")
        print("  - pg_dump -U username -h host database_name > backup.sql")

        print("\nMySQL:")
        print("  - mysqldump -u username -p database_name > backup.sql")

        print("\nSQLite:")
        print("  - cp database.db database_backup.db")

        print("\nMongoDB:")
        print("  - mongodump --db database_name --out backup_directory")

        print("\nFor application-level backup (using SQLAlchemy):")
        print("  - Use your ORM's capabilities to extract data")
        print("  - Serialize data to JSON or other formats")

        input("\nPress Enter to continue...")

    def run_database_restore(self) -> None:
        """Restore database from backup"""
        print("\n" + "="*70)
        print("DATABASE RESTORE")
        print("="*70)

        print("\nDatabase restore functionality depends on the specific database system.")
        print("Here are common approaches for different databases:")

        print("\nPostgreSQL:")
        print("  - psql -U username -h host database_name < backup.sql")

        print("\nMySQL:")
        print("  - mysql -u username -p database_name < backup.sql")

        print("\nSQLite:")
        print("  - cp backup_database.db database.db")

        print("\nMongoDB:")
        print("  - mongorestore backup_directory/")

        print("\n⚠️  Warning: Restoring will overwrite current data!")
        print("Always ensure you have the correct backup file before proceeding.")

        input("\nPress Enter to continue...")
class DatabaseMenu(Menu):
    """Menu for database tools"""

    def __init__(self):
        self.database = DatabaseTools()
        super().__init__("Database Management Tools")

    def setup_items(self) -> None:
        """Setup menu items for database tools"""
        self.items = [
            MenuItem("Setup Database Configuration", self.database.setup_database_config),
            MenuItem("Run Database Migrations", self.database.run_database_migrations),
            MenuItem("Seed Database with Data", self.database.seed_database),
            MenuItem("Compare Database Schemas", self.database.compare_database_schemas),
            MenuItem("Create Database Backup", self.database.run_database_backup),
            MenuItem("Restore Database from Backup", self.database.run_database_restore),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]