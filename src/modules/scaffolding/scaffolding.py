"""
Scaffolding Module
Creates advanced project templates for various development frameworks
"""
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator


class ScaffoldingTools:
    """Handles project scaffolding and template creation"""

    def __init__(self):
        self.validator = SecurityValidator()

    def create_python_project(self) -> None:
        """Create a Python project with standard structure"""
        print("\n" + "="*70)
        print("PYTHON PROJECT SCAFFOLDING")
        print("="*70)
        
        try:
            project_name = input("Enter project name: ").strip()
            if not project_name:
                print("Project name cannot be empty!")
                input("\nPress Enter to continue...")
                return
            
            # Validate project name
            if not self.validator.validate_file_name(project_name):
                print("Invalid project name!")
                input("\nPress Enter to continue...")
                return
            
            # Create project directory
            project_dir = Path(project_name)
            if project_dir.exists():
                print(f"Project directory '{project_name}' already exists!")
                input("\nPress Enter to continue...")
                return
            
            project_dir.mkdir()
            
            # Create standard Python project structure
            dirs_to_create = [
                project_dir / "src",
                project_dir / project_name.replace("-", "_"),  # package dir (with hyphens replaced by underscores)
                project_dir / "tests",
                project_dir / "docs",
                project_dir / "scripts",
                project_dir / ".github" / "workflows",
            ]
            
            for directory in dirs_to_create:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Create pyproject.toml
            pyproject_content = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A new Python project"
readme = "README.md"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}}
]
dependencies = [
    # Add your runtime dependencies here
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
    "flake8>=4.0",
    "mypy>=0.950",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
]

[tool.setuptools.packages.find]
where = ["src"]
'''
            
            with open(project_dir / "pyproject.toml", "w") as f:
                f.write(pyproject_content)
            
            # Create README.md
            readme_content = f"""# {project_name}

## Description
A brief description of your project.

## Installation
```bash
pip install -e .
```

## Usage
Explain how to use your project.

## Contributing
Instructions for contributing to the project.

## License
MIT License
"""
            
            with open(project_dir / "README.md", "w") as f:
                f.write(readme_content)
            
            # Create main package init
            main_pkg_dir = project_dir / project_name.replace("-", "_")
            with open(main_pkg_dir / "__init__.py", "w") as f:
                f.write('"""Main package for {project_name}"""\n')
            
            # Create a main module
            with open(main_pkg_dir / "main.py", "w") as f:
                f.write(f'''"""
Main module for {project_name}
"""

def main():
    """Main entry point"""
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
''')
            
            # Create basic test
            with open(project_dir / "tests" / "test_main.py", "w") as f:
                f.write(f'''"""
Basic tests for {project_name}
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_import():
    """Test that the main module can be imported"""
    try:
        from {project_name.replace("-", "_")} import main
        assert hasattr(main, 'main')
    except ImportError:
        assert False, "Could not import main module"

if __name__ == "__main__":
    test_import()
    print("All tests passed!")
''')
            
            # Create .gitignore
            gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre checker
.pyre/
"""
            
            with open(project_dir / ".gitignore", "w") as f:
                f.write(gitignore_content)
            
            print(f"\n✓ Python project '{project_name}' created successfully!")
            print(f"  Directory structure:")
            print(f"  ├── src/")
            print(f"  ├── tests/")
            print(f"  ├── docs/")
            print(f"  ├── pyproject.toml")
            print(f"  ├── README.md")
            print(f"  └── .gitignore")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as e:
            print(f"\n⚠ Error creating Python project: {e}")
        
        input("\nPress Enter to continue...")

    def create_fastapi_project(self) -> None:
        """Create a FastAPI project template"""
        print("\n" + "="*70)
        print("FASTAPI PROJECT SCAFFOLDING")
        print("="*70)
        
        try:
            project_name = input("Enter project name: ").strip()
            if not project_name:
                print("Project name cannot be empty!")
                input("\nPress Enter to continue...")
                return
            
            # Validate project name
            if not self.validator.validate_file_name(project_name):
                print("Invalid project name!")
                input("\nPress Enter to continue...")
                return
            
            # Create project directory
            project_dir = Path(project_name)
            if project_dir.exists():
                print(f"Project directory '{project_name}' already exists!")
                input("\nPress Enter to continue...")
                return
            
            project_dir.mkdir()
            
            # Create FastAPI project structure
            dirs_to_create = [
                project_dir / "src",
                project_dir / project_name.replace("-", "_"),
                project_dir / "src" / "api",
                project_dir / "src" / "models", 
                project_dir / "src" / "schemas",
                project_dir / "src" / "database",
                project_dir / "src" / "routers",
                project_dir / "src" / "utils",
                project_dir / "tests",
                project_dir / "config",
            ]
            
            for directory in dirs_to_create:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Create main.py for FastAPI app
            main_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import items

app = FastAPI(
    title="My FastAPI Project",
    description="A simple FastAPI project generated by Magic CLI",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api/v1", tags=["items"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
'''
            
            with open(project_dir / "src" / "main.py", "w") as f:
                f.write(main_content)
            
            # Create pyproject.toml
            pyproject_content = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A FastAPI project"
readme = "README.md"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}}
]
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.22.0",
    "pydantic>=2.0",
    "sqlalchemy>=2.0",
    "psycopg2-binary>=2.9.0",  # For PostgreSQL
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
    "flake8>=4.0",
    "mypy>=0.950",
    "httpx>=0.24.0",  # For testing
]
test = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
    "httpx>=0.24.0",
]

[project.scripts]
start = "src.main:run_server"

[tool.setuptools.packages.find]
where = ["src"]
'''
            
            with open(project_dir / "pyproject.toml", "w") as f:
                f.write(pyproject_content)
            
            # Create README.md
            readme_content = f"""# {project_name} - FastAPI Project

## Description
A FastAPI project generated by Magic CLI.

## Installation
```bash
pip install -e .
```

## Running the Application
```bash
# Development
uvicorn src.main:app --reload

# Production (using the start command)
start
```

## API Documentation
- Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Alternative docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure
```
src/
├── main.py             # Main FastAPI application
├── api/                # API-related modules
├── models/             # Database models
├── schemas/            # Pydantic schemas
├── database/           # Database configuration
├── routers/            # API routes
└── utils/              # Utility functions
```

## Contributing
Instructions for contributing to the project.

## License
MIT License
"""
            
            with open(project_dir / "README.md", "w") as f:
                f.write(readme_content)
            
            # Create a basic router
            router_content = '''from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from src.database import get_db
from src import schemas

router = APIRouter()

# Example endpoint
@router.get("/", response_model=List[schemas.Item])
def get_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve items.
    """
    # items = crud.get_items(db, skip=skip, limit=limit)
    # return items
    return []

@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """
    Create an item.
    """
    # return crud.create_item(db=db, item=item)
    return item
'''
            
            with open(project_dir / "src" / "routers" / "items.py", "w") as f:
                f.write(router_content)
            
            # Create a basic Pydantic schema
            schema_content = '''from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
'''
            
            with open(project_dir / "src" / "schemas" / "items.py", "w") as f:
                f.write(schema_content)
            
            # Create a basic database setup
            db_content = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
            
            with open(project_dir / "src" / "database" / "database.py", "w") as f:
                f.write(db_content)
            
            # Create .gitignore
            gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.dev
.env.prod

# FastAPI / Uvicorn
*.db
*.db-journal

# Coverage
.coverage
htmlcov/

# Pytest
.pytest_cache/

# VSCode
.vscode/
"""
            
            with open(project_dir / ".gitignore", "w") as f:
                f.write(gitignore_content)
            
            print(f"\n✓ FastAPI project '{project_name}' created successfully!")
            print(f"  Directory structure:")
            print(f"  ├── src/")
            print(f"  │   ├── main.py")
            print(f"  │   ├── api/")
            print(f"  │   ├── models/")
            print(f"  │   ├── schemas/")
            print(f"  │   ├── database/")
            print(f"  │   ├── routers/")
            print(f"  │   └── utils/")
            print(f"  ├── tests/")
            print(f"  ├── config/")
            print(f"  ├── pyproject.toml")
            print(f"  ├── README.md")
            print(f"  └── .gitignore")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as e:
            print(f"\n⚠ Error creating FastAPI project: {e}")
        
        input("\nPress Enter to continue...")

    def create_react_project(self) -> None:
        """Create a React project template"""
        print("\n" + "="*70)
        print("REACT PROJECT SCAFFOLDING")
        print("="*70)
        
        print("\nThis feature would create a React project using Create React App.")
        print("It requires Node.js and npm to be installed on your system.")
        
        try:
            # Check if Node.js is available
            node_result = subprocess.run(['node', '--version'], 
                                        capture_output=True, text=True)
            
            if node_result.returncode != 0:
                print("\n⚠ Node.js is not installed or not in PATH")
                print("Please install Node.js to use this feature")
                input("\nPress Enter to continue...")
                return
            
            project_name = input("Enter project name: ").strip()
            if not project_name:
                print("Project name cannot be empty!")
                input("\nPress Enter to continue...")
                return
            
            # Validate project name
            if not self.validator.validate_file_name(project_name):
                print("Invalid project name!")
                input("\nPress Enter to continue...")
                return
            
            # Create project directory
            project_dir = Path(project_name)
            if project_dir.exists():
                print(f"Project directory '{project_name}' already exists!")
                input("\nPress Enter to continue...")
                return
            
            # Create React app
            print(f"\nCreating React app '{project_name}'...")
            result = subprocess.run([
                'npx', 'create-react-app', project_name, 
                '--template', 'typescript'  # Using TypeScript template
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"\n⚠ Error creating React app: {result.stderr}")
                input("\nPress Enter to continue...")
                return
            
            # Add Magic CLI specific configurations
            # Add a custom README with Magic CLI notes
            readme_path = project_dir / "README.md"
            with open(readme_path, "r") as f:
                original_readme = f.read()
            
            magic_cli_readme = f"""# {project_name} - Created with Magic CLI

This project was created using Magic CLI's React project generator.

## Original Create React App README

{original_readme}
"""
            
            with open(readme_path, "w") as f:
                f.write(magic_cli_readme)
            
            print(f"\n✓ React project '{project_name}' created successfully!")
            print("Project includes TypeScript template")
            print("\nTo start the development server:")
            print(f"  cd {project_name}")
            print("  npm start")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except FileNotFoundError:
            print("\n⚠ 'npx' command not found. Make sure Node.js is installed.")
        except Exception as e:
            print(f"\n⚠ Error creating React project: {e}")
        
        input("\nPress Enter to continue...")

    def create_flutter_project(self) -> None:
        """Create a Flutter project template"""
        print("\n" + "="*70)
        print("FLUTTER PROJECT SCAFFOLDING")
        print("="*70)
        
        print("\nThis feature would create a Flutter project.")
        print("It requires Flutter SDK to be installed on your system.")
        
        try:
            # Check if Flutter is available
            flutter_result = subprocess.run(['flutter', '--version'], 
                                          capture_output=True, text=True)
            
            if flutter_result.returncode != 0:
                print("\n⚠ Flutter is not installed or not in PATH")
                print("Please install Flutter SDK to use this feature")
                input("\nPress Enter to continue...")
                return
            
            project_name = input("Enter project name: ").strip()
            if not project_name:
                print("Project name cannot be empty!")
                input("\nPress Enter to continue...")
                return
            
            # Validate project name
            if not self.validator.validate_file_name(project_name):
                print("Invalid project name!")
                input("\nPress Enter to continue...")
                return
            
            # Create project directory
            project_dir = Path(project_name)
            if project_dir.exists():
                print(f"Project directory '{project_name}' already exists!")
                input("\nPress Enter to continue...")
                return
            
            # Create Flutter app
            print(f"\nCreating Flutter app '{project_name}'...")
            result = subprocess.run([
                'flutter', 'create', project_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"\n⚠ Error creating Flutter app: {result.stderr}")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n✓ Flutter project '{project_name}' created successfully!")
            print("\nTo run the app:")
            print(f"  cd {project_name}")
            print("  flutter run")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except FileNotFoundError:
            print("\n⚠ 'flutter' command not found. Make sure Flutter SDK is installed.")
        except Exception as e:
            print(f"\n⚠ Error creating Flutter project: {e}")
        
        input("\nPress Enter to continue...")

    def create_docker_project(self) -> None:
        """Create Docker configuration files for a project"""
        print("\n" + "="*70)
        print("DOCKER CONFIGURATION SCAFFOLDING")
        print("="*70)
        
        print("\nCreating Docker configuration files...")
        
        # Create Dockerfile
        dockerfile_content = '''# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.main:app"]
'''
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Create docker-compose.yml
        compose_content = '''version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    volumes:
      - .:/app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=hello_world_dev
      - POSTGRES_USER=hello_world
      - POSTGRES_PASSWORD=hello_world
    ports:
      - "5432:5432"

volumes:
  postgres_data:
'''
        
        with open("docker-compose.yml", "w") as f:
            f.write(compose_content)
        
        # Create .dockerignore
        dockerignore_content = """# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
.pytest_cache
.coverage

# Virtual Environment
venv
env
ENV

# IDE
.vscode
.idea

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment variables
.env
"""
        
        with open(".dockerignore", "w") as f:
            f.write(dockerignore_content)
        
        print("\n✓ Docker configuration files created successfully!")
        print("  - Dockerfile: Basic Python application container")
        print("  - docker-compose.yml: Multi-container setup with database")
        print("  - .dockerignore: Ignore unnecessary files in Docker build")
        print("\nTo build and run:")
        print("  docker-compose up --build")
        
        input("\nPress Enter to continue...")


class ScaffoldingMenu(Menu):
    """Menu for scaffolding tools"""

    def __init__(self):
        self.scaffolding = ScaffoldingTools()
        super().__init__("Project Scaffolding Tools")

    def setup_items(self) -> None:
        """Setup menu items for scaffolding tools"""
        self.items = [
            MenuItem("Create Python Project", self.scaffolding.create_python_project),
            MenuItem("Create FastAPI Project", self.scaffolding.create_fastapi_project),
            MenuItem("Create React Project", self.scaffolding.create_react_project),
            MenuItem("Create Flutter Project", self.scaffolding.create_flutter_project),
            MenuItem("Create Docker Configuration", self.scaffolding.create_docker_project),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]