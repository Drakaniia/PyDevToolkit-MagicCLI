"""
Backend Framework Integration Tools
Comprehensive framework-specific automation and helpers
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.menu import Menu, MenuItem


class FrameworkTools(Menu):
    """Backend Framework Integration Tools Menu"""

    def __init__(self):
        super().__init__("Backend Framework Tools")

    def setup_items(self):
        """Setup framework tools menu items"""
        if self.items:
            return

        self.items = [
            MenuItem("FastAPI Project Setup", self._setup_fastapi),
            MenuItem("Django/Flask Management", self._manage_django_flask),
            MenuItem("Spring Boot Configuration", self._configure_spring_boot),
            MenuItem("Express.js Helpers", self._express_helpers),
            MenuItem("Framework Migration Tools", self._framework_migration),
            MenuItem("Code Generators", self._code_generators),
            MenuItem("Back to Backend Dev", self._back_to_backend)
        ]

    def _setup_fastapi(self):
        """Setup FastAPI project"""
        self.clear_screen()
        print("=" * 60)
        print("  FastAPI Project Setup")
        print("=" * 60)
        
        project_name = input("Enter project name: ")
        
        print(f"\nSetting up FastAPI project: {project_name}")
        
        # Create project structure
        project_structure = {
            f"{project_name}": {
                "app": {
                    "__init__.py": "",
                    "main.py": self._get_fastapi_main_content(project_name),
                    "config.py": self._get_fastapi_config_content(),
                    "database.py": self._get_fastapi_database_content(),
                    "models": {
                        "__init__.py": "",
                        "base.py": self._get_fastapi_base_model_content()
                    },
                    "schemas": {
                        "__init__.py": "",
                        "user.py": self._get_fastapi_user_schema_content()
                    },
                    "api": {
                        "__init__.py": "",
                        "deps.py": self._get_fastapi_deps_content(),
                        "v1": {
                            "__init__.py": "",
                            "api.py": self._get_fastapi_api_content(),
                            "endpoints": {
                                "__init__.py": "",
                                "users.py": self._get_fastapi_users_endpoint_content()
                            }
                        }
                    },
                    "core": {
                        "__init__.py": "",
                        "config.py": self._get_fastapi_core_config_content(),
                        "security.py": self._get_fastapi_security_content()
                    }
                },
                "tests": {
                    "__init__.py": "",
                    "test_main.py": self._get_fastapi_test_content(),
                    "conftest.py": self._get_fastapi_conftest_content()
                },
                "requirements.txt": self._get_fastapi_requirements(),
                ".env.example": self._get_fastapi_env_example(),
                "alembic.ini": self._get_fastapi_alembic_config(),
                "Dockerfile": self._get_fastapi_dockerfile(),
                "docker-compose.yml": self._get_fastapi_docker_compose()
            }
        }
        
        self._create_project_structure(project_structure)
        
        print("FastAPI project setup completed!")
        print(f" Project created: {project_name}/")
        print(" Run: cd {} && uvicorn app.main:app --reload".format(project_name))
        
        input("\nPress Enter to continue...")
        return None

    def _get_fastapi_main_content(self, project_name):
        return f'''"""
FastAPI Main Application
{project_name} - Auto-generated FastAPI project
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "message": "Welcome to {project_name} API",
        "version": settings.VERSION,
        "docs": "/docs"
    }}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy"}}
'''

    def _get_fastapi_config_content(self):
        return '''"""
FastAPI Configuration
"""
from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Auto-generated FastAPI application"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"

settings = Settings()
'''

    def _get_fastapi_database_content(self):
        return '''"""
Database Configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

    def _get_fastapi_base_model_content(self):
        return '''"""
Base Model for FastAPI
"""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''

    def _get_fastapi_user_schema_content(self):
        return '''"""
User Schemas for FastAPI
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
'''

    def _get_fastapi_deps_content(self):
        return '''"""
FastAPI Dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # user = db.query(User).filter(User.id == payload.get("user_id")).first()
    # if user is None:
    #     raise credentials_exception
    
    # return user
    return payload  # Return payload for now
'''

    def _get_fastapi_api_content(self):
        return '''"""
FastAPI API Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
'''

    def _get_fastapi_users_endpoint_content(self):
        return '''"""
Users Endpoint for FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user import User, UserCreate
from app.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all users"""
    # users = db.query(User).offset(skip).limit(limit).all()
    # return users
    return []  # Placeholder

@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create new user"""
    # db_user = db.query(User).filter(User.email == user.email).first()
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user logic here
    return user  # Placeholder

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: dict = Depends(get_current_user)
):
    """Get current user"""
    return current_user
'''

    def _get_fastapi_core_config_content(self):
        return '''"""
Core Configuration for FastAPI
"""
from pydantic import BaseSettings

class CoreSettings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        case_sensitive = True
'''

    def _get_fastapi_security_content(self):
        return '''"""
Security Utilities for FastAPI
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
'''

    def _get_fastapi_test_content(self):
        return '''"""
Tests for FastAPI
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
'''

    def _get_fastapi_conftest_content(self):
        return '''"""
Pytest Configuration for FastAPI
"""
import pytest
from app.database import Base, engine, get_db
from sqlalchemy.orm import Session

@pytest.fixture(scope="session")
def db():
    """Database fixture"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db):
    """Database session fixture"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
'''

    def _get_fastapi_requirements(self):
        return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
alembic==1.13.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
'''

    def _get_fastapi_env_example(self):
        return '''# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
'''

    def _get_fastapi_alembic_config(self):
        return '''# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format.  This value may be specified
# in several ways:
#
# 1. A Python strftime() format string for the date/time portion,
#    which will be combined with a UUID for uniqueness:
#    version_num_format = %%Y%%m%%d_%%H%%M%%S
#
# 2. A function defined in the script.py.mako template
#    which can be used to apply custom formatting to the version number.
#    Example: version_num_format = ${my_custom_format_function}
#
# 3. An absolute path to a Python file containing a function
#    called "format_version_num" which takes a RevisionContext
#    as an argument and returns a string.
#    Example: version_num_format = /path/to/myfile.py
#
# If left blank, a UUID will be used.
# version_num_format =

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = sqlite:///./app.db


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''

    def _get_fastapi_dockerfile(self):
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

    def _get_fastapi_docker_compose(self):
        return '''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./app.db:/app/app.db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: fastapi_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''

    def _manage_django_flask(self):
        """Manage Django/Flask projects"""
        self.clear_screen()
        print("=" * 60)
        print("  Django/Flask Management")
        print("=" * 60)
        
        print("\nSelect framework:")
        print("1. Django")
        print("2. Flask")
        print("3. Django REST Framework")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._manage_django()
            elif choice == 2:
                self._manage_flask()
            elif choice == 3:
                self._manage_drf()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _manage_django(self):
        """Django management tools"""
        print("\nDjango Management Tools")
        print("1. Create Django project")
        print("2. Generate Django app")
        print("3. Create Django models")
        print("4. Setup Django admin")
        
        choice = input("\nEnter choice: ")
        if choice == "1":
            self._create_django_project()
        elif choice == "2":
            self._create_django_app()
        elif choice == "3":
            self._create_django_models()
        elif choice == "4":
            self._setup_django_admin()

    def _create_django_project(self):
        """Create Django project"""
        project_name = input("Enter project name: ")
        print(f"\nCreating Django project: {project_name}")
        
        django_settings_content = f'''"""
Django Settings for {project_name}
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

AUTH_PASSWORD_VALIDATORS = [
    {{
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
]
'''
        
        with open('django_settings.py', 'w') as f:
            f.write(django_settings_content)
        
        print("Django project template created!")

    def _create_django_app(self):
        """Create Django app"""
        app_name = input("Enter app name: ")
        print(f"\nCreating Django app: {app_name}")
        
        # Create app structure
        app_structure = {
            app_name: {
                "__init__.py": "",
                "admin.py": self._get_django_admin_content(app_name),
                "apps.py": self._get_django_apps_content(app_name),
                "models.py": self._get_django_models_content(app_name),
                "tests.py": self._get_django_tests_content(app_name),
                "views.py": self._get_django_views_content(app_name),
                "urls.py": self._get_django_urls_content(app_name),
                "serializers.py": self._get_django_serializers_content(app_name),
                "migrations": {
                    "__init__.py": ""
                }
            }
        }
        
        self._create_project_structure(app_structure)
        print(f"Django app '{app_name}' created!")

    def _get_django_admin_content(self, app_name):
        return f'''"""
Django Admin for {app_name}
"""
from django.contrib import admin
from .models import {app_name.title()}

@admin.register({app_name.title()})
class {app_name.title()}Admin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
'''

    def _get_django_apps_content(self, app_name):
        return f'''"""
Django App Configuration for {app_name}
"""
from django.apps import AppConfig

class {app_name.title()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
'''

    def _get_django_models_content(self, app_name):
        return f'''"""
Django Models for {app_name}
"""
from django.db import models

class {app_name.title()}(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "{app_name.title()}"
        verbose_name_plural = "{app_name.title()}s"
    
    def __str__(self):
        return self.name
'''

    def _get_django_tests_content(self, app_name):
        return f'''"""
Tests for {app_name}
"""
from django.test import TestCase
from .models import {app_name.title()}

class {app_name.title()}TestCase(TestCase):
    def test_{app_name}_creation(self):
        """Test {app_name} creation"""
        {app_name} = {app_name.title()}.objects.create(
            name="Test {app_name.title()}",
            description="Test description"
        )
        self.assertEqual({app_name}.name, "Test {app_name.title()}")
        self.assertTrue({app_name}.is_active)
'''

    def _get_django_views_content(self, app_name):
        return f'''"""
Django Views for {app_name}
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import {app_name.title()}
from .serializers import {app_name.title()}Serializer

class {app_name.title()}ViewSet(viewsets.ModelViewSet):
    """{app_name.title()} ViewSet"""
    queryset = {app_name.title()}.objects.all()
    serializer_class = {app_name.title()}Serializer
    permission_classes = [IsAuthenticated]
'''

    def _get_django_urls_content(self, app_name):
        return f'''"""
Django URLs for {app_name}
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import {app_name.title()}ViewSet

router = DefaultRouter()
router.register(r'{app_name}s', {app_name.title()}ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
'''

    def _get_django_serializers_content(self, app_name):
        return f'''"""
Django Serializers for {app_name}
"""
from rest_framework import serializers
from .models import {app_name.title()}

class {app_name.title()}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {app_name.title()}
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
'''

    def _manage_flask(self):
        """Flask management tools"""
        print("\n Flask Management Tools")
        print("1. Create Flask app")
        print("2. Add Flask extensions")
        print("3. Create Flask blueprints")
        
        choice = input("\nEnter choice: ")
        if choice == "1":
            self._create_flask_app()
        elif choice == "2":
            self._add_flask_extensions()
        elif choice == "3":
            self._create_flask_blueprints()

    def _create_flask_app(self):
        """Create Flask application"""
        app_name = input("Enter app name: ")
        print(f"\n Creating Flask app: {app_name}")
        
        flask_app_content = f'''"""
Flask Application: {app_name}
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
'''
        
        with open('app.py', 'w') as f:
            f.write(flask_app_content)
        
        print("Flask application created!")

    def _manage_drf(self):
        """Django REST Framework management"""
        print("\nDjango REST Framework Tools")
        print("1. Create DRF ViewSets")
        print("2. Create DRF Serializers")
        print("3. Setup DRF authentication")
        
        choice = input("\nEnter choice: ")
        if choice == "1":
            self._create_drf_viewsets()
        elif choice == "2":
            self._create_drf_serializers()
        elif choice == "3":
            self._setup_drf_auth()

    def _configure_spring_boot(self):
        """Configure Spring Boot project"""
        self.clear_screen()
        print("=" * 60)
        print("  Spring Boot Configuration")
        print("=" * 60)
        
        project_name = input("Enter project name: ")
        package_name = input("Enter package name (e.g., com.example.app): ")
        
        print(f"\nConfiguring Spring Boot project: {project_name}")
        
        # Create Spring Boot structure
        spring_structure = {
            "src": {
                "main": {
                    "java": {
                        package_name.replace('.', '/'): {
                            f"{project_name.title()}Application.java": self._get_spring_main_content(package_name),
                            "config": {
                                "SecurityConfig.java": self._get_spring_security_content(package_name),
                                "DatabaseConfig.java": self._get_spring_database_content(package_name)
                            },
                            "controller": {
                                "UserController.java": self._get_spring_controller_content(package_name)
                            },
                            "model": {
                                "User.java": self._get_spring_model_content(package_name)
                            },
                            "repository": {
                                "UserRepository.java": self._get_spring_repository_content(package_name)
                            },
                            "service": {
                                "UserService.java": self._get_spring_service_content(package_name)
                            }
                        }
                    },
                    "resources": {
                        "application.properties": self._get_spring_properties_content(),
                        "application-dev.properties": self._get_spring_dev_properties_content(),
                        "application-prod.properties": self._get_spring_prod_properties_content()
                    }
                }
            },
            "pom.xml": self._get_spring_pom_content(project_name, package_name)
        }
        
        self._create_project_structure(spring_structure)
        print("Spring Boot project configured!")
        
        input("\nPress Enter to continue...")
        return None

    def _get_spring_main_content(self, package_name):
        return f'''package {package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {package_name.split('.')[-1].title()}Application {{
    public static void main(String[] args) {{
        SpringApplication.run({package_name.split('.')[-1].title()}Application.class, args);
    }}
}}
'''

    def _get_spring_security_content(self, package_name):
        return f'''package {package_name}.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {{
    
    @Bean
    public PasswordEncoder passwordEncoder() {{
        return new BCryptPasswordEncoder();
    }}
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http
            .csrf().disable()
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .httpBasic();
        
        return http.build();
    }}
}}
'''

    def _get_spring_database_content(self, package_name):
        return f'''package {package_name}.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@Configuration
@EntityScan(basePackages = "{package_name}.model")
@EnableJpaRepositories(basePackages = "{package_name}.repository")
public class DatabaseConfig {{
    // Database configuration
}}
'''

    def _get_spring_controller_content(self, package_name):
        return f'''package {package_name}.controller;

import {package_name}.service.UserService;
import {package_name}.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {{
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public List<User> getAllUsers() {{
        return userService.getAllUsers();
    }}
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {{
        return userService.getUserById(id);
    }}
    
    @PostMapping
    public User createUser(@RequestBody User user) {{
        return userService.createUser(user);
    }}
    
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {{
        return userService.updateUser(id, user);
    }}
    
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {{
        userService.deleteUser(id);
    }}
}}
'''

    def _get_spring_model_content(self, package_name):
        return f'''package {package_name}.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {{
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String username;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(nullable = false)
    private String password;
    
    @Column(name = "first_name")
    private String firstName;
    
    @Column(name = "last_name")
    private String lastName;
    
    @Column(nullable = false)
    private Boolean active = true;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {{
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }}
    
    @PreUpdate
    protected void onUpdate() {{
        updatedAt = LocalDateTime.now();
    }}
    
    // Getters and Setters
    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id = id; }}
    
    public String getUsername() {{ return username; }}
    public void setUsername(String username) {{ this.username = username; }}
    
    public String getEmail() {{ return email; }}
    public void setEmail(String email) {{ this.email = email; }}
    
    public String getPassword() {{ return password; }}
    public void setPassword(String password) {{ this.password = password; }}
    
    public String getFirstName() {{ return firstName; }}
    public void setFirstName(String firstName) {{ this.firstName = firstName; }}
    
    public String getLastName() {{ return lastName; }}
    public void setLastName(String lastName) {{ this.lastName = lastName; }}
    
    public Boolean getActive() {{ return active; }}
    public void setActive(Boolean active) {{ this.active = active; }}
    
    public LocalDateTime getCreatedAt() {{ return createdAt; }}
    public void setCreatedAt(LocalDateTime createdAt) {{ this.createdAt = createdAt; }}
    
    public LocalDateTime getUpdatedAt() {{ return updatedAt; }}
    public void setUpdatedAt(LocalDateTime updatedAt) {{ this.updatedAt = updatedAt; }}
}}
'''

    def _get_spring_repository_content(self, package_name):
        return f'''package {package_name}.repository;

import {package_name}.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {{
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}}
'''

    def _get_spring_service_content(self, package_name):
        return f'''package {package_name}.service;

import {package_name}.model.User;
import {package_name}.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {{
    
    @Autowired
    private UserRepository userRepository;
    
    public List<User> getAllUsers() {{
        return userRepository.findAll();
    }}
    
    public User getUserById(Long id) {{
        return userRepository.findById(id).orElse(null);
    }}
    
    public User createUser(User user) {{
        return userRepository.save(user);
    }}
    
    public User updateUser(Long id, User userDetails) {{
        User user = userRepository.findById(id).orElse(null);
        if (user != null) {{
            user.setUsername(userDetails.getUsername());
            user.setEmail(userDetails.getEmail());
            user.setFirstName(userDetails.getFirstName());
            user.setLastName(userDetails.getLastName());
            return userRepository.save(user);
        }}
        return null;
    }}
    
    public void deleteUser(Long id) {{
        userRepository.deleteById(id);
    }}
}}
'''

    def _get_spring_properties_content(self):
        return '''# Spring Boot Configuration
spring.application.name=spring-boot-app
server.port=8080

# Database Configuration
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=password
spring.h2.console.enabled=true

# JPA Configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# Logging
logging.level.org.springframework=INFO
logging.level.com.example=DEBUG
'''

    def _get_spring_dev_properties_content(self):
        return '''# Development Configuration
spring.profiles.active=dev
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true
logging.level.org.springframework=DEBUG
'''

    def _get_spring_prod_properties_content(self):
        return '''# Production Configuration
spring.profiles.active=prod
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.show-sql=false
logging.level.org.springframework=WARN
'''

    def _get_spring_pom_content(self, project_name, package_name):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    
    <groupId>{package_name}</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0</version>
    <name>{project_name}</name>
    <description>Spring Boot Application</description>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
'''

    def _express_helpers(self):
        """Express.js helpers and generators"""
        self.clear_screen()
        print("=" * 60)
        print("  Express.js Helpers")
        print("=" * 60)
        
        print("\nExpress.js Tools:")
        print("1. Create Express.js app")
        print("2. Add middleware")
        print("3. Create routes")
        print("4. Setup database integration")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._create_express_app()
            elif choice == 2:
                self._add_express_middleware()
            elif choice == 3:
                self._create_express_routes()
            elif choice == 4:
                self._setup_express_database()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _create_express_app(self):
        """Create Express.js application"""
        app_name = input("Enter app name: ")
        print(f"\nCreating Express.js app: {app_name}")
        
        express_app_content = f'''/**
 * Express.js Application: {app_name}
 * Auto-generated Express.js application
 */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({{ limit: '10mb' }}));
app.use(express.urlencoded({{ extended: true }}));

// Routes
app.use('/api/users', require('./routes/users'));
app.use('/api/auth', require('./routes/auth'));

// Health check endpoint
app.get('/health', (req, res) => {{
    res.status(200).json({{
        status: 'OK',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    }});
}});

// Root endpoint
app.get('/', (req, res) => {{
    res.json({{
        message: 'Welcome to {app_name} API',
        version: '1.0.0',
        docs: '/api-docs'
    }});
}});

// Error handling middleware
app.use((err, req, res, next) => {{
    console.error(err.stack);
    res.status(500).json({{
        error: 'Something went wrong!',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
    }});
}});

// 404 handler
app.use('*', (req, res) => {{
    res.status(404).json({{
        error: 'Not Found',
        message: 'The requested resource was not found'
    }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(` Server running on port ${{PORT}}`);
    console.log(` API documentation: http://localhost:${{PORT}}/api-docs`);
}});

module.exports = app;
'''
        
        with open('app.js', 'w') as f:
            f.write(express_app_content)
        
        # Create package.json
        package_json_content = f'''{{
  "name": "{app_name}",
  "version": "1.0.0",
  "description": "Auto-generated Express.js application",
  "main": "app.js",
  "scripts": {{
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "jest",
    "test:watch": "jest --watch"
  }},
  "dependencies": {{
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "mongoose": "^8.0.3",
    "express-validator": "^7.0.1"
  }},
  "devDependencies": {{
    "nodemon": "^3.0.2",
    "jest": "^29.7.0",
    "supertest": "^6.3.3"
  }},
  "keywords": ["express", "node", "api"],
  "author": "",
  "license": "MIT"
}}
'''
        
        with open('package.json', 'w') as f:
            f.write(package_json_content)
        
        print("Express.js application created!")

    def _framework_migration(self):
        """Framework migration tools"""
        self.clear_screen()
        print("=" * 60)
        print("  Framework Migration Tools")
        print("=" * 60)
        
        print("\nMigration Options:")
        print("1. Flask to FastAPI")
        print("2. Express.js to NestJS")
        print("3. Django to Flask")
        print("4. Custom migration script")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._migrate_flask_to_fastapi()
            elif choice == 2:
                self._migrate_express_to_nestjs()
            elif choice == 3:
                self._migrate_django_to_flask()
            elif choice == 4:
                self._custom_migration()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _code_generators(self):
        """Code generators for various frameworks"""
        self.clear_screen()
        print("=" * 60)
        print("  Code Generators")
        print("=" * 60)
        
        print("\nCode Generation Options:")
        print("1. Generate CRUD operations")
        print("2. Generate API documentation")
        print("3. Generate database models")
        print("4. Generate test cases")
        
        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._generate_crud()
            elif choice == 2:
                self._generate_api_docs()
            elif choice == 3:
                self._generate_db_models()
            elif choice == 4:
                self._generate_tests()
        except ValueError:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        return None

    def _create_project_structure(self, structure, base_path="."):
        """Create project structure from dictionary"""
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                self._create_project_structure(content, path)
            else:
                with open(path, 'w') as f:
                    f.write(content)

    def _back_to_backend(self):
        """Return to backend development menu"""
        return "exit"