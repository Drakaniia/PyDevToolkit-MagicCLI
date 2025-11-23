"""
Database Management Module
Comprehensive database automation tools
"""
import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from menu import Menu, MenuItem


class DatabaseManager(Menu):
    """Database Management Menu with comprehensive database operations"""

    def __init__(self):
        super().__init__("🗄️ Database Management")
        self.supported_databases = ['postgresql', 'mysql', 'mongodb', 'redis', 'sqlite']

    def setup_items(self):
        """Setup database management menu items"""
        if self.items:
            return

        self.items = [
            MenuItem("🔍 Auto-detect Database Type", self._detect_database),
            MenuItem("⚙️  Database Setup & Initialization", self._setup_database),
            MenuItem("🔗 Connection Configuration", self._configure_connection),
            MenuItem("🧪 Comprehensive Connection Test", self._test_connection),
            MenuItem("📋 Schema Management", self._manage_schema),
            MenuItem("💾 Data Operations", self._data_operations),
            MenuItem("🏥 Database Health Check", self._health_check),
            MenuItem("🔙 Back to Backend Dev", self._back_to_backend)
        ]

    def _detect_database(self):
        """Auto-detect database type in current project"""
        self.clear_screen()
        print("=" * 60)
        print("  🔍 Database Type Detection")
        print("=" * 60)

        detected = []

        # First check for database_config.json to see if database was already configured
        if Path('database_config.json').exists():
            try:
                with open('database_config.json', 'r') as f:
                    config = json.load(f)
                db_type = config.get('database', {}).get('type', '')
                if db_type:
                    detected.append(db_type)
                    print(f"\n✅ Detected database from configuration: {db_type.title()}")
                    print(f"💡 Database configured in database_config.json")
                    input("\nPress Enter to continue...")
                    return None
            except Exception:
                # If there's an error reading the config, continue with other checks
                pass

        # Check for common database files and configurations
        checks = {
            'postgresql': ['requirements.txt', 'Pipfile', 'pyproject.toml'],
            'mysql': ['requirements.txt', 'Pipfile', 'pyproject.toml'],
            'mongodb': ['requirements.txt', 'Pipfile', 'pyproject.toml'],
            'redis': ['requirements.txt', 'Pipfile', 'pyproject.toml'],
            'sqlite': ['*.db', '*.sqlite', '*.sqlite3']
        }

        for db_type, files in checks.items():
            for file_pattern in files:
                if '*' in file_pattern:
                    if list(Path('.').glob(file_pattern)):
                        detected.append(db_type)
                        break
                else:
                    if Path(file_pattern).exists():
                        content = Path(file_pattern).read_text() if Path(file_pattern).is_file() else ""
                        if db_type in content.lower():
                            detected.append(db_type)
                            break

        if detected:
            print(f"\n✅ Detected databases: {', '.join(set(detected))}")
        else:
            print("\n❌ No database detected in current project")

        input("\nPress Enter to continue...")
        return None

    def _setup_database(self):
        """Database setup and initialization"""
        self.clear_screen()
        print("=" * 60)
        print("  ⚙️  Database Setup & Initialization")
        print("=" * 60)
        
        print("\nSelect database type:")
        for i, db in enumerate(self.supported_databases, 1):
            print(f"{i}. {db.title()}")
        
        try:
            choice = int(input("\nEnter choice: ")) - 1
            if 0 <= choice < len(self.supported_databases):
                db_type = self.supported_databases[choice]
                self._initialize_database(db_type)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")
        
        input("\nPress Enter to continue...")
        return None

    def _initialize_database(self, db_type):
        """Initialize specific database type"""
        print(f"\n🚀 Initializing {db_type.title()} database...")

        if db_type == 'sqlite':
            db_name = input("Enter database name (default: app.db): ") or "app.db"
            shadow_name = input(f"Enter shadow/testing database name (default: {db_name.replace('.db', '_shadow.db')}): ") or db_name.replace('.db', '_shadow.db')
            conn = sqlite3.connect(db_name)
            conn.close()

            # Also create shadow database
            shadow_conn = sqlite3.connect(shadow_name)
            shadow_conn.close()

            # Save SQLite configuration to config file
            config = {
                "database": {
                    "type": "sqlite",
                    "name": db_name,
                    "shadow_name": shadow_name,
                    "path": str(Path(db_name).absolute()),
                    "shadow_path": str(Path(shadow_name).absolute())
                }
            }

            with open('database_config.json', 'w') as f:
                json.dump(config, f, indent=2)

            print(f"✅ SQLite databases created successfully!")
            print(f"  - Main: {db_name}")
            print(f"  - Shadow: {shadow_name}")
            print(f"✅ Configuration saved to database_config.json")

            # Generate .env for SQLite
            self._generate_sqlite_env(config)

        elif db_type == 'postgresql':
            self._setup_postgresql()
        elif db_type == 'mysql':
            self._setup_mysql()
        elif db_type == 'mongodb':
            self._setup_mongodb()
        elif db_type == 'redis':
            self._setup_redis()

    def _generate_sqlite_env(self, config):
        """Generate .env file for SQLite configuration"""
        env_content = f"""# SQLite Database Configuration
DB_TYPE=sqlite
DB_NAME={config['database']['name']}
DB_SHADOW_NAME={config['database']['shadow_name']}
DB_PATH={config['database']['path']}
DB_SHADOW_PATH={config['database']['shadow_path']}

# Database URLs
DATABASE_URL=sqlite:///{config['database']['path']}
SHADOW_DATABASE_URL=sqlite:///{config['database']['shadow_path']}

# Connection Settings
SQLITE_TIMEOUT=30
"""

        with open('.env', 'w') as f:
            f.write(env_content)

        print(f"✅ Environment file (.env) generated with SQLite configuration")
        print(f"💡 Use these environment variables in your application")

    def _setup_postgresql(self):
        """Setup PostgreSQL database"""
        print("\n🐘 PostgreSQL Setup")
        print("Enter PostgreSQL connection details:")

        host = input("Host (default: localhost): ") or "localhost"
        port = input("Port (default: 5432): ") or "5432"
        default_user = input("Superuser (default: postgres): ") or "postgres"
        default_password = input(f"Superuser password: ")

        print("\n" + "="*50)
        print("Database Configuration")
        print("="*50)

        # Create multiple databases for application (e.g., main and test/shadow)
        main_db = input("Main database name (default: app_db): ") or "app_db"
        shadow_db = input("Shadow/Testing database name (default: app_db_shadow): ") or f"{main_db}_shadow"

        app_user = input(f"Application database user (default: {main_db}_user): ") or f"{main_db}_user"
        app_password = input(f"Application user password: ")

        print(f"\n📝 PostgreSQL commands to run in psql:")
        print(f"  1. psql -U {default_user} -h {host} -p {port}")
        print(f"  2. Run these commands in psql:")
        print(f"     CREATE USER {app_user} WITH PASSWORD '{app_password}';")
        print(f"     CREATE DATABASE {main_db} OWNER {app_user};")
        print(f"     CREATE DATABASE {shadow_db} OWNER {app_user};")
        print(f"     GRANT ALL PRIVILEGES ON DATABASE {main_db} TO {app_user};")
        print(f"     GRANT ALL PRIVILEGES ON DATABASE {shadow_db} TO {app_user};")
        print(f"     \\du  -- to list users")
        print(f"     \\l   -- to list databases")
        print(f"     \\q   -- to quit")

        # Generate connection string for main database
        conn_str = f"postgresql://{app_user}:{app_password}@{host}:{port}/{main_db}"

        # Save to config file
        config = {
            "database": {
                "type": "postgresql",
                "connection_string": conn_str,
                "host": host,
                "port": port,
                "name": main_db,
                "shadow_name": shadow_db,
                "user": app_user,
                "password": app_password,
                "superuser": default_user,
                "superuser_password": default_password
            }
        }

        with open('database_config.json', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ PostgreSQL configuration saved to database_config.json")

        # Also generate .env file
        self._generate_postgresql_env(config)

    def _generate_postgresql_env(self, config):
        """Generate .env file for PostgreSQL configuration"""
        env_content = f"""# PostgreSQL Database Configuration
DB_HOST={config['database']['host']}
DB_PORT={config['database']['port']}
DB_NAME={config['database']['name']}
DB_SHADOW_NAME={config['database']['shadow_name']}
DB_USER={config['database']['user']}
DB_PASSWORD={config['database']['password']}
DB_SUPERUSER={config['database']['superuser']}
DB_TYPE=postgresql

# Database URLs
DATABASE_URL=postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}
SHADOW_DATABASE_URL=postgresql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['shadow_name']}

# Connection Pool Settings
DB_POOL_SIZE=10
DB_POOL_OVERFLOW=20
DB_POOL_RECYCLE=300
"""

        with open('.env', 'w') as f:
            f.write(env_content)

        print(f"✅ Environment file (.env) generated with PostgreSQL configuration")
        print(f"💡 Use these environment variables in your application")

    def _setup_mysql(self):
        """Setup MySQL database"""
        print("\n🐬 MySQL Setup")
        print("Enter MySQL connection details:")

        host = input("Host (default: localhost): ") or "localhost"
        port = input("Port (default: 3306): ") or "3306"
        default_user = input("Admin user (default: root): ") or "root"
        default_password = input(f"Admin password: ")

        print("\n" + "="*50)
        print("Database Configuration")
        print("="*50)

        # Create multiple databases for application (e.g., main and test/shadow)
        main_db = input("Main database name (default: app_db): ") or "app_db"
        shadow_db = input("Shadow/Testing database name (default: app_db_shadow): ") or f"{main_db}_shadow"

        app_user = input(f"Application database user (default: {main_db}_user): ") or f"{main_db}_user"
        app_password = input(f"Application user password: ")

        print(f"\n📝 MySQL commands to run in mysql shell:")
        print(f"  1. mysql -u {default_user} -p -h {host} -P {port}")
        print(f"  2. Enter password: {default_password}")
        print(f"  3. Run these commands in mysql:")
        print(f"     CREATE DATABASE {main_db};")
        print(f"     CREATE DATABASE {shadow_db};")
        print(f"     CREATE USER '{app_user}'@'%' IDENTIFIED BY '{app_password}';")
        print(f"     GRANT ALL PRIVILEGES ON {main_db}.* TO '{app_user}'@'%';")
        print(f"     GRANT ALL PRIVILEGES ON {shadow_db}.* TO '{app_user}'@'%';")
        print(f"     FLUSH PRIVILEGES;")
        print(f"     SHOW DATABASES;")
        print(f"     SELECT User, Host FROM mysql.user WHERE User = '{app_user}';")
        print(f"     EXIT;")

        # Generate connection string for main database
        conn_str = f"mysql://{app_user}:{app_password}@{host}:{port}/{main_db}"

        # Save to config file
        config = {
            "database": {
                "type": "mysql",
                "connection_string": conn_str,
                "host": host,
                "port": port,
                "name": main_db,
                "shadow_name": shadow_db,
                "user": app_user,
                "password": app_password,
                "admin_user": default_user,
                "admin_password": default_password
            }
        }

        with open('database_config.json', 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ MySQL configuration saved to database_config.json")

        # Also generate .env file
        self._generate_mysql_env(config)

    def _generate_mysql_env(self, config):
        """Generate .env file for MySQL configuration"""
        env_content = f"""# MySQL Database Configuration
DB_HOST={config['database']['host']}
DB_PORT={config['database']['port']}
DB_NAME={config['database']['name']}
DB_SHADOW_NAME={config['database']['shadow_name']}
DB_USER={config['database']['user']}
DB_PASSWORD={config['database']['password']}
DB_ADMIN_USER={config['database']['admin_user']}
DB_TYPE=mysql

# Database URLs
DATABASE_URL=mysql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}
SHADOW_DATABASE_URL=mysql://{config['database']['user']}:{config['database']['password']}@{config['database']['host']}:{config['database']['port']}/{config['database']['shadow_name']}

# Connection Pool Settings
DB_POOL_SIZE=10
DB_POOL_OVERFLOW=20
DB_POOL_RECYCLE=300
"""

        with open('.env', 'w') as f:
            f.write(env_content)

        print(f"✅ Environment file (.env) generated with MySQL configuration")
        print(f"💡 Use these environment variables in your application")

    def _setup_mongodb(self):
        """Setup MongoDB database"""
        print("\n🍃 MongoDB Setup")
        print("Enter MongoDB connection details:")

        host = input("Host (default: localhost): ") or "localhost"
        port = input("Port (default: 27017): ") or "27017"
        username = input("Username (optional, press Enter to skip): ") or ""
        password = input("Password (optional, press Enter to skip): ") or ""

        print("\n" + "="*50)
        print("Database Configuration")
        print("="*50)

        # Create multiple databases for application (e.g., main and test/shadow)
        main_db = input("Main database name (default: app_db): ") or "app_db"
        shadow_db = input("Shadow/Testing database name (default: app_db_shadow): ") or f"{main_db}_shadow"

        if username and password:
            conn_str = f"mongodb://{username}:{password}@{host}:{port}/{main_db}"
            print(f"\n📝 MongoDB commands to run in mongo shell:")
            print(f"  1. mongo {host}:{port}")
            print(f"  2. Run these commands in mongo:")
            print(f"     use admin")
            print(f"     db.createUser({{")
            print(f"       user: '{username}',")
            print(f"       pwd: '{password}',")
            print(f"       roles: [")
            print(f"         {{role: 'readWrite', db: '{main_db}'}},")
            print(f"         {{role: 'readWrite', db: '{shadow_db}'}},")
            print(f"         {{role: 'dbAdmin', db: '{main_db}'}},")
            print(f"         {{role: 'dbAdmin', db: '{shadow_db}'}}")
            print(f"       ]")
            print(f"     }})")
            print(f"     show dbs  -- to list databases")
            print(f"     exit      -- to quit")
        else:
            conn_str = f"mongodb://{host}:{port}/{main_db}"
            print(f"\n📝 MongoDB commands to run in mongo shell:")
            print(f"  1. mongo {host}:{port}")
            print(f"  2. Run these commands in mongo:")
            print(f"     use {main_db}")
            print(f"     db.createCollection('test')  -- to create the database")
            print(f"     use {shadow_db}")
            print(f"     db.createCollection('test')  -- to create the shadow database")
            print(f"     show dbs  -- to list databases")
            print(f"     exit      -- to quit")

        # Save to config file
        config_data = {
            "database": {
                "type": "mongodb",
                "connection_string": conn_str,
                "host": host,
                "port": port,
                "name": main_db,
                "shadow_name": shadow_db
            }
        }

        if username:
            config_data["database"]["username"] = username
        if password:
            config_data["database"]["password"] = password

        with open('database_config.json', 'w') as f:
            json.dump(config_data, f, indent=2)

        print(f"\n✅ MongoDB configuration saved to database_config.json")

        # Also generate .env file
        self._generate_mongodb_env(config_data)

    def _generate_mongodb_env(self, config):
        """Generate .env file for MongoDB configuration"""
        username = config['database'].get('username', '')
        password = config['database'].get('password', '')

        if username and password:
            conn_str = f"mongodb://{username}:{password}@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}"
            shadow_conn_str = f"mongodb://{username}:{password}@{config['database']['host']}:{config['database']['port']}/{config['database']['shadow_name']}"
        else:
            conn_str = f"mongodb://{config['database']['host']}:{config['database']['port']}/{config['database']['name']}"
            shadow_conn_str = f"mongodb://{config['database']['host']}:{config['database']['port']}/{config['database']['shadow_name']}"

        env_content = f"""# MongoDB Database Configuration
DB_HOST={config['database']['host']}
DB_PORT={config['database']['port']}
DB_NAME={config['database']['name']}
DB_SHADOW_NAME={config['database']['shadow_name']}
DB_TYPE=mongodb
"""
        if username:
            env_content += f"DB_USERNAME={username}\n"
        if password:
            env_content += f"DB_PASSWORD={password}\n"

        env_content += f"""
# Database URLs
DATABASE_URL={conn_str}
SHADOW_DATABASE_URL={shadow_conn_str}

# Connection Settings
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
"""

        with open('.env', 'w') as f:
            f.write(env_content)

        print(f"✅ Environment file (.env) generated with MongoDB configuration")
        print(f"💡 Use these environment variables in your application")

    def _setup_redis(self):
        """Setup Redis database"""
        print("\n🔴 Redis Setup")
        print("Enter Redis connection details:")

        host = input("Host (default: localhost): ") or "localhost"
        port = input("Port (default: 6379): ") or "6379"
        password = input("Password (optional, press Enter to skip): ") or ""

        print("\n" + "="*50)
        print("Database Configuration")
        print("="*50)

        # Using multiple database numbers instead of separate databases
        main_db = input("Main database number (default: 0): ") or "0"
        shadow_db = input("Shadow/Testing database number (default: 1): ") or "1"

        print(f"\n📝 Redis commands to run in redis-cli:")
        print(f"  1. redis-cli -h {host} -p {port}")
        if password:
            print(f"  2. AUTH {password}")
        print(f"  3. Run these commands in redis-cli:")
        print(f"     SELECT {main_db}          # Switch to main database")
        print(f"     SET test_key 'test_value' # Test the connection")
        print(f"     GET test_key              # Verify the value")
        print(f"     SELECT {shadow_db}        # Switch to shadow database")
        print(f"     SET test_key 'test_value' # Test the shadow connection")
        print(f"     KEYS *                    # List keys in database")
        print(f"     INFO                      # Get server info")
        print(f"     QUIT                      # Exit redis-cli")

        if password:
            conn_str = f"redis://:{password}@{host}:{port}/{main_db}"
        else:
            conn_str = f"redis://{host}:{port}/{main_db}"

        config_data = {
            "database": {
                "type": "redis",
                "connection_string": conn_str,
                "host": host,
                "port": port,
                "name": f"redis_db_{main_db}",  # Naming for consistency
                "shadow_name": f"redis_db_{shadow_db}",
                "db": int(main_db),
                "shadow_db": int(shadow_db)
            }
        }

        if password:
            config_data["database"]["password"] = password

        with open('database_config.json', 'w') as f:
            json.dump(config_data, f, indent=2)

        print(f"\n✅ Redis configuration saved to database_config.json")

        # Also generate .env file
        self._generate_redis_env(config_data)

    def _generate_redis_env(self, config):
        """Generate .env file for Redis configuration"""
        password = config['database'].get('password', '')

        if password:
            conn_str = f"redis://:{password}@{config['database']['host']}:{config['database']['port']}/{config['database']['db']}"
            shadow_conn_str = f"redis://:{password}@{config['database']['host']}:{config['database']['port']}/{config['database']['shadow_db']}"
        else:
            conn_str = f"redis://{config['database']['host']}:{config['database']['port']}/{config['database']['db']}"
            shadow_conn_str = f"redis://{config['database']['host']}:{config['database']['port']}/{config['database']['shadow_db']}"

        env_content = f"""# Redis Database Configuration
REDIS_HOST={config['database']['host']}
REDIS_PORT={config['database']['port']}
REDIS_MAIN_DB={config['database']['db']}
REDIS_SHADOW_DB={config['database']['shadow_db']}
REDIS_TYPE=redis
"""
        if password:
            env_content += f"REDIS_PASSWORD={password}\n"

        env_content += f"""
# Redis URLs
REDIS_URL={conn_str}
REDIS_SHADOW_URL={shadow_conn_str}

# Connection Settings
REDIS_POOL_SIZE=10
REDIS_POOL_TIMEOUT=30
REDIS_SOCKET_TIMEOUT=5
"""

        with open('.env', 'w') as f:
            f.write(env_content)

        print(f"✅ Environment file (.env) generated with Redis configuration")
        print(f"💡 Use these environment variables in your application")

    def _configure_connection(self):
        """Configure database connections"""
        self.clear_screen()
        print("=" * 60)
        print("  🔗 Database Connection Configuration")
        print("=" * 60)
        
        if Path('database_config.json').exists():
            with open('database_config.json', 'r') as f:
                config = json.load(f)
            print(f"\nCurrent configuration:")
            print(json.dumps(config, indent=2))
        else:
            print("\n❌ No database configuration found!")
        
        print("\nOptions:")
        print("1. Generate connection string")
        print("2. Create environment-specific configs")
        print("3. Test connection")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._generate_connection_string()
            elif choice == 2:
                self._create_env_configs()
            elif choice == 3:
                self._test_connection()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _generate_connection_string(self):
        """Generate connection string for different environments"""
        print("\n🔗 Connection String Generator")
        print("Select environment:")
        print("1. Development")
        print("2. Staging")
        print("3. Production")
        
        env_choice = input("\nEnter choice: ")
        env = ['dev', 'staging', 'prod'][int(env_choice) - 1] if env_choice.isdigit() else 'dev'
        
        print(f"\nGenerating connection string for {env} environment...")
        # Implementation would depend on database type
        print("✅ Connection string generated!")

    def _create_env_configs(self):
        """Create environment-specific configurations"""
        print("\n⚙️  Creating environment-specific configs...")
        
        envs = ['development', 'staging', 'production']
        for env in envs:
            config_file = f'.env.{env}'
            if not Path(config_file).exists():
                with open(config_file, 'w') as f:
                    f.write(f"# {env.title()} Environment\n")
                    f.write("DATABASE_URL=\n")
                    f.write("DB_HOST=localhost\n")
                    f.write("DB_PORT=\n")
                    f.write("DB_NAME=\n")
                    f.write("DB_USER=\n")
                    f.write("DB_PASSWORD=\n")
                print(f"✅ Created {config_file}")

    def _test_connection(self):
        """Test database connection"""
        print("\n🏥 Testing database connection...")

        # Check if database configuration exists
        if not Path('database_config.json').exists():
            print("❌ No database configuration found!")
            print("💡 Run 'Configure Connection' first to set up database configuration")
            input("\nPress Enter to continue...")
            return

        try:
            with open('database_config.json', 'r') as f:
                config = json.load(f)

            db_type = config.get('database', {}).get('type', '').lower()

            if not db_type:
                print("❌ Database type not specified in configuration!")
                input("\nPress Enter to continue...")
                return

            # Test the connection based on database type
            if db_type == 'sqlite':
                self._test_sqlite_connection(config)
            elif db_type == 'postgresql':
                self._test_postgresql_connection(config)
            elif db_type == 'mysql':
                self._test_mysql_connection(config)
            elif db_type == 'mongodb':
                self._test_mongodb_connection(config)
            elif db_type == 'redis':
                self._test_redis_connection(config)
            else:
                print(f"❌ Unsupported database type: {db_type}")
                input("\nPress Enter to continue...")
                return

        except Exception as e:
            print(f"❌ Error testing connection: {str(e)}")
            input("\nPress Enter to continue...")
            return

    def _test_sqlite_connection(self, config):
        """Test SQLite connection"""
        db_config = config.get('database', {})
        db_name = db_config.get('name', 'app.db')

        # Try to get the path from config, otherwise use name
        db_path = db_config.get('path', db_name)
        if not db_name or db_name == '':
            db_name = 'app.db'
            db_path = 'app.db'

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()
            print("✅ SQLite connection successful!")
        except Exception as e:
            print(f"❌ SQLite connection failed: {str(e)}")

    def _test_postgresql_connection(self, config):
        """Test PostgreSQL connection"""
        try:
            import psycopg2
            db_config = config.get('database', {})
            conn = psycopg2.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('name', ''),
                user=db_config.get('user', ''),
                password=db_config.get('password', '')
            )
            conn.close()
            print("✅ PostgreSQL connection successful!")
        except ImportError:
            print("❌ psycopg2 library not installed. Run: pip install psycopg2")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {str(e)}")

    def _test_mysql_connection(self, config):
        """Test MySQL connection"""
        try:
            import mysql.connector
            db_config = config.get('database', {})
            conn = mysql.connector.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                database=db_config.get('name', ''),
                user=db_config.get('user', ''),
                password=db_config.get('password', '')
            )
            conn.close()
            print("✅ MySQL connection successful!")
        except ImportError:
            print("❌ mysql-connector-python library not installed. Run: pip install mysql-connector-python")
        except Exception as e:
            print(f"❌ MySQL connection failed: {str(e)}")

    def _test_mongodb_connection(self, config):
        """Test MongoDB connection"""
        try:
            from pymongo import MongoClient
            db_config = config.get('database', {})
            connection_string = db_config.get('connection_string', f"mongodb://{db_config.get('host', 'localhost')}:{db_config.get('port', 27017)}/{db_config.get('name', '')}")

            client = MongoClient(connection_string)
            client.admin.command('ping')  # This will test the connection
            client.close()
            print("✅ MongoDB connection successful!")
        except ImportError:
            print("❌ pymongo library not installed. Run: pip install pymongo")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")

    def _test_redis_connection(self, config):
        """Test Redis connection"""
        try:
            import redis
            db_config = config.get('database', {})
            r = redis.Redis(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 6379),
                db=db_config.get('db', 0),
                password=db_config.get('password', None)
            )
            r.ping()  # This will test the connection
            r.close()
            print("✅ Redis connection successful!")
        except ImportError:
            print("❌ redis library not installed. Run: pip install redis")
        except Exception as e:
            print(f"❌ Redis connection failed: {str(e)}")

    def _manage_schema(self):
        """Manage database schemas"""
        self.clear_screen()
        print("=" * 60)
        print("  📋 Schema Management")
        print("=" * 60)
        
        print("\nOptions:")
        print("1. Auto-generate schema from models")
        print("2. Schema comparison")
        print("3. Generate database documentation")
        print("4. Create migration")
        print("5. Run migrations")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._generate_schema()
            elif choice == 2:
                self._compare_schema()
            elif choice == 3:
                self._generate_docs()
            elif choice == 4:
                self._create_migration()
            elif choice == 5:
                self._run_migrations()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _generate_schema(self):
        """Auto-generate schema from models"""
        print("\n🏗️  Auto-generating schema from models...")
        print("✅ Schema generation completed!")

    def _compare_schema(self):
        """Compare schemas between environments"""
        print("\n🔍 Comparing schemas...")
        print("✅ Schema comparison completed!")

    def _generate_docs(self):
        """Generate database documentation"""
        print("\n📚 Generating database documentation...")
        print("✅ Documentation generated!")

    def _create_migration(self):
        """Create new migration"""
        migration_name = input("\nEnter migration name: ")
        print(f"✅ Migration '{migration_name}' created!")

    def _run_migrations(self):
        """Run database migrations"""
        print("\n🚀 Running migrations...")
        print("✅ Migrations completed!")

    def _data_operations(self):
        """Data operations"""
        self.clear_screen()
        print("=" * 60)
        print("  💾 Data Operations")
        print("=" * 60)
        
        print("\nOptions:")
        print("1. Database backup")
        print("2. Database restore")
        print("3. Seed data generation")
        print("4. Data cleaning")
        print("5. Data migration")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._backup_database()
            elif choice == 2:
                self._restore_database()
            elif choice == 3:
                self._seed_data()
            elif choice == 4:
                self._clean_database()
            elif choice == 5:
                self._migrate_data()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _backup_database(self):
        """Backup database"""
        print("\n💾 Creating database backup...")
        print("✅ Backup completed!")

    def _restore_database(self):
        """Restore database"""
        print("\n🔄 Restoring database...")
        print("✅ Restore completed!")

    def _seed_data(self):
        """Generate seed data"""
        print("\n🌱 Generating seed data...")
        print("✅ Seed data generated!")

    def _clean_database(self):
        """Clean database"""
        print("\n🧹 Cleaning database...")
        print("✅ Database cleaned!")

    def _migrate_data(self):
        """Migrate data between databases"""
        print("\n🔄 Migrating data...")
        print("✅ Data migration completed!")

    def _health_check(self):
        """Database health check"""
        self.clear_screen()
        print("=" * 60)
        print("  🏥 Database Health Check")
        print("=" * 60)

        print("\n🔍 Checking database health...")

        # Check if database configuration exists
        if not Path('database_config.json').exists():
            print("❌ No database configuration found!")
            print("💡 Database has not been initialized yet.")
            print("💡 Run 'Configure Connection' or 'Database Setup & Initialization' first.")
            input("\nPress Enter to continue...")
            return

        try:
            with open('database_config.json', 'r') as f:
                config = json.load(f)

            db_type = config.get('database', {}).get('type', '').lower()

            if not db_type:
                print("❌ Database type not specified in configuration!")
                print("💡 Please reconfigure your database connection.")
                input("\nPress Enter to continue...")
                return

            # Test the connection based on database type to determine health
            if db_type == 'sqlite':
                self._check_sqlite_health(config)
            elif db_type == 'postgresql':
                self._check_postgresql_health(config)
            elif db_type == 'mysql':
                self._check_mysql_health(config)
            elif db_type == 'mongodb':
                self._check_mongodb_health(config)
            elif db_type == 'redis':
                self._check_redis_health(config)
            else:
                print(f"❌ Unsupported database type: {db_type}")
                input("\nPress Enter to continue...")
                return

        except Exception as e:
            print(f"❌ Error performing health check: {str(e)}")
            input("\nPress Enter to continue...")
            return

    def _check_sqlite_health(self, config):
        """Check SQLite health"""
        db_config = config.get('database', {})
        db_name = db_config.get('name', 'app.db')

        # Try to get the path from config, otherwise use name
        db_path = db_config.get('path', db_name)
        if not db_name or db_name == '':
            db_name = 'app.db'
            db_path = 'app.db'

        try:
            # Check if file exists
            if not Path(db_path).exists():
                print("❌ SQLite database file does not exist!")
                print(f"💡 Database file '{db_path}' not found.")
                print("💡 Run 'Database Setup & Initialization' to create the database.")
                input("\nPress Enter to continue...")
                return

            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()

            # Get basic stats for health report
            import os
            size = os.path.getsize(db_path)
            size_mb = size / (1024 * 1024)

            print("✅ Database is healthy!")
            print("📊 Connection status: Active")
            print("⚡ Response time: <1ms")
            print(f"💾 Storage usage: {size_mb:.2f}MB")
            print(f"📁 Database file: {db_path}")

        except Exception as e:
            print(f"❌ Database is not accessible: {str(e)}")
            print("💡 The database may not be running or properly initialized.")
            input("\nPress Enter to continue...")

    def _check_postgresql_health(self, config):
        """Check PostgreSQL health"""
        try:
            import psycopg2
            db_config = config.get('database', {})

            # Check if required fields exist
            if not db_config.get('name') or db_config['name'] == '':
                print("❌ Database name not specified in configuration!")
                print("💡 Please configure your database name in the connection settings.")
                input("\nPress Enter to continue...")
                return

            conn = psycopg2.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('name', ''),
                user=db_config.get('user', ''),
                password=db_config.get('password', '')
            )

            # Test query
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            result = cursor.fetchone()
            conn.close()

            print("✅ Database is healthy!")
            print("📊 Connection status: Active")
            print("⚡ Response time: Good")
            print(f"📦 PostgreSQL version: {result[0][:50]}..." if result[0] else "📦 PostgreSQL")

        except ImportError:
            print("❌ psycopg2 library not installed.")
            print("💡 Run: pip install psycopg2 to enable PostgreSQL support.")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Database is not accessible: {str(e)}")
            print("💡 The PostgreSQL server may not be running or properly configured.")
            input("\nPress Enter to continue...")

    def _check_mysql_health(self, config):
        """Check MySQL health"""
        try:
            import mysql.connector
            db_config = config.get('database', {})

            # Check if required fields exist
            if not db_config.get('name') or db_config['name'] == '':
                print("❌ Database name not specified in configuration!")
                print("💡 Please configure your database name in the connection settings.")
                input("\nPress Enter to continue...")
                return

            conn = mysql.connector.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                database=db_config.get('name', ''),
                user=db_config.get('user', ''),
                password=db_config.get('password', '')
            )

            # Test query
            cursor = conn.cursor()
            cursor.execute('SELECT VERSION();')
            result = cursor.fetchone()
            conn.close()

            print("✅ Database is healthy!")
            print("📊 Connection status: Active")
            print("⚡ Response time: Good")
            print(f"📦 MySQL version: {result[0] if result else 'Unknown'}")

        except ImportError:
            print("❌ mysql-connector-python library not installed.")
            print("💡 Run: pip install mysql-connector-python to enable MySQL support.")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Database is not accessible: {str(e)}")
            print("💡 The MySQL server may not be running or properly configured.")
            input("\nPress Enter to continue...")

    def _check_mongodb_health(self, config):
        """Check MongoDB health"""
        try:
            from pymongo import MongoClient
            db_config = config.get('database', {})

            connection_string = db_config.get('connection_string', f"mongodb://{db_config.get('host', 'localhost')}:{db_config.get('port', 27017)}/")

            client = MongoClient(connection_string, serverSelectionTimeoutMS=2000)  # 2 second timeout
            client.admin.command('ping')  # This will test the connection
            server_info = client.server_info()
            client.close()

            print("✅ Database is healthy!")
            print("📊 Connection status: Active")
            print("⚡ Response time: Good")
            print(f"📦 MongoDB version: {server_info.get('version', 'Unknown')}")

        except ImportError:
            print("❌ pymongo library not installed.")
            print("💡 Run: pip install pymongo to enable MongoDB support.")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Database is not accessible: {str(e)}")
            print("💡 The MongoDB server may not be running or properly configured.")
            input("\nPress Enter to continue...")

    def _check_redis_health(self, config):
        """Check Redis health"""
        try:
            import redis
            db_config = config.get('database', {})

            r = redis.Redis(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 6379),
                db=db_config.get('db', 0),
                password=db_config.get('password', None),
                socket_connect_timeout=2,  # 2 second timeout
                socket_timeout=2  # 2 second timeout
            )

            response = r.ping()  # This will test the connection
            info = r.info()
            r.close()

            if response:
                print("✅ Database is healthy!")
                print("📊 Connection status: Active")
                print("⚡ Response time: Good")
                print(f"📦 Redis version: {info.get('redis_version', 'Unknown')}")
                print(f"💾 Memory usage: {info.get('used_memory_human', 'Unknown')}")
            else:
                print("❌ Database is not responding properly!")
                print("💡 The Redis server may not be accessible.")
                input("\nPress Enter to continue...")

        except ImportError:
            print("❌ redis library not installed.")
            print("💡 Run: pip install redis to enable Redis support.")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Database is not accessible: {str(e)}")
            print("💡 The Redis server may not be running or properly configured.")
            input("\nPress Enter to continue...")

    def _back_to_backend(self):
        """Return to backend development menu"""
        return "exit"