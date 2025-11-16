"""
automation/dev_mode/docker_quick.py
Quick Docker commands for development
"""
import subprocess
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from . import _base

# Import security and logging modules inside functions to avoid circular imports
from . import menu_utils
from ._base import DevModeCommand
from .menu_utils import get_choice_with_arrows


class DockerQuickCommand(DevModeCommand):
    """Command for quick Docker operations"""
    
    label = "Docker Quick Commands"
    description = "Common Docker operations for development"
    
    def run(self, interactive: bool = True, **kwargs) -> any:
        """Execute Docker command"""
        if interactive:
            return self._interactive_docker()
        else:
            return self._noninteractive_docker(**kwargs)
    
    def _interactive_docker(self):
        """Interactive Docker operations"""
        print("\n" + "="*70)
        print("🐳 DOCKER QUICK COMMANDS")
        print("="*70 + "\n")
        
        # Check if Docker is installed
        if not self.validate_binary('docker'):
            self.show_missing_binary_error(
                'docker',
                'https://www.docker.com/get-started'
            )
            input("\nPress Enter to continue...")
            return
        
        # Check if Docker is running
        if not self._is_docker_running():
            print("⚠️  Docker daemon is not running")
            print("💡 Start Docker Desktop or run: sudo systemctl start docker")
            input("\nPress Enter to continue...")
            return
        
        # Show Docker operations menu with arrow navigation
        docker_options = [
            "Initialize (docker init)",
            "Build Image",
            "Run Container", 
            "Stop Container",
            "List Running Containers",
            "List All Containers",
            "List Images",
            "Docker Compose",
            "Container Orchestration (Swarm)",
            "Prune Unused Resources",
            "Cancel"
        ]
        
        choice = get_choice_with_arrows(docker_options, "Docker Operations")
        
        if choice == 1:
            self._docker_init()
        elif choice == 2:
            self._build_image()
        elif choice == 3:
            self._run_container()
        elif choice == 4:
            self._stop_container()
        elif choice == 5:
            self._list_containers(all_containers=False)
        elif choice == 6:
            self._list_containers(all_containers=True)
        elif choice == 7:
            self._list_images()
        elif choice == 8:
            self._docker_compose_menu()
        elif choice == 9:
            self._container_orchestration_menu()
        elif choice == 10:
            self._prune_resources()
        elif choice == 11:
            print("\n❌ Operation cancelled")
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")
    
    def _docker_init(self):
        """Initialize Docker for the project with intelligent defaults"""
        print("\n🐳 DOCKER INITIALIZE")
        print("="*70 + "\n")
        
        # Detect project type and structure
        project_info = self._detect_project_type()
        
        print(f"📋 Detected project type: {project_info['type']}")
        if project_info['framework']:
            print(f"🔧 Framework: {project_info['framework']}")
        print()
        
        # Get build output directory
        build_dir = self._prompt_build_directory(project_info)
        
        # Get start command
        start_command = self._prompt_start_command(project_info)
        
        # Get port
        port = self._prompt_port(project_info)
        
        # Generate Dockerfile if it doesn't exist
        dockerfile_path = Path("Dockerfile")
        if not dockerfile_path.exists():
            print(f"\n📝 Generating Dockerfile for {project_info['type']} project...")
            self._generate_dockerfile(project_info, build_dir, start_command, port)
            print("✅ Dockerfile created successfully!")
        else:
            print(f"\n⚠️  Dockerfile already exists at {dockerfile_path}")
            overwrite = input("Do you want to overwrite it? (y/n, default: n): ").strip().lower()
            if overwrite in ['y', 'yes']:
                self._generate_dockerfile(project_info, build_dir, start_command, port)
                print("✅ Dockerfile updated successfully!")
        
        # Optionally generate .dockerignore
        dockerignore_path = Path(".dockerignore")
        if not dockerignore_path.exists():
            generate_ignore = input("\n📝 Generate .dockerignore file? (y/n, default: y): ").strip().lower()
            if generate_ignore != 'n' and generate_ignore != 'no':
                self._generate_dockerignore(project_info)
                print("✅ .dockerignore created successfully!")
        
        # Summary
        print(f"\n🎉 Docker initialization complete!")
        print(f"📁 Build directory: {build_dir}")
        print(f"🚀 Start command: {start_command}")
        print(f"🌐 Port: {port}")
        
        # Offer to build image now
        build_now = input(f"\n🔨 Build Docker image now? (y/n, default: y): ").strip().lower()
        if build_now != 'n' and build_now != 'no':
            project_name = Path.cwd().name.lower()
            self._build_image(interactive=False, 
                            image_name=f"{project_name}:latest", 
                            dockerfile="Dockerfile", 
                            context=".")
    
    def _detect_project_type(self) -> Dict[str, str]:
        """Detect project type and framework"""
        cwd = Path.cwd()
        project_info = {
            'type': 'unknown',
            'framework': '',
            'build_tool': '',
            'package_manager': ''
        }
        
        # Check for Node.js projects
        package_json = cwd / "package.json"
        if package_json.exists():
            project_info['type'] = 'nodejs'
            project_info['package_manager'] = 'npm'
            
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                    
                # Check for package managers
                if (cwd / "yarn.lock").exists():
                    project_info['package_manager'] = 'yarn'
                elif (cwd / "pnpm-lock.yaml").exists():
                    project_info['package_manager'] = 'pnpm'
                
                # Detect framework from dependencies
                deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                
                if 'vite' in deps:
                    project_info['framework'] = 'vite'
                elif 'next' in deps:
                    project_info['framework'] = 'nextjs'
                elif 'nuxt' in deps:
                    project_info['framework'] = 'nuxtjs'
                elif 'react' in deps:
                    project_info['framework'] = 'react'
                elif 'vue' in deps:
                    project_info['framework'] = 'vue'
                elif 'angular' in deps or '@angular/core' in deps:
                    project_info['framework'] = 'angular'
                elif 'express' in deps:
                    project_info['framework'] = 'express'
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Check for Python projects
        elif (cwd / "requirements.txt").exists() or (cwd / "setup.py").exists() or (cwd / "pyproject.toml").exists():
            project_info['type'] = 'python'
            
            # Check for specific Python frameworks
            requirements_files = [cwd / "requirements.txt", cwd / "requirements-test.txt"]
            for req_file in requirements_files:
                if req_file.exists():
                    try:
                        content = req_file.read_text()
                        if 'django' in content.lower():
                            project_info['framework'] = 'django'
                        elif 'flask' in content.lower():
                            project_info['framework'] = 'flask'
                        elif 'fastapi' in content.lower():
                            project_info['framework'] = 'fastapi'
                    except:
                        pass
        
        # Check for Java projects
        elif (cwd / "pom.xml").exists():
            project_info['type'] = 'java'
            project_info['build_tool'] = 'maven'
        elif (cwd / "build.gradle").exists() or (cwd / "build.gradle.kts").exists():
            project_info['type'] = 'java'
            project_info['build_tool'] = 'gradle'
        
        # Check for Go projects
        elif (cwd / "go.mod").exists():
            project_info['type'] = 'go'
        
        # Check for Rust projects
        elif (cwd / "Cargo.toml").exists():
            project_info['type'] = 'rust'
        
        return project_info
    
    def _prompt_build_directory(self, project_info: Dict[str, str]) -> str:
        """Prompt for build output directory with intelligent defaults"""
        print("📁 Build Output Directory")
        print("-" * 25)
        
        # Auto-detect common build directories
        common_dirs = ['dist', 'build', 'out', 'public', 'static', 'target/classes']
        detected_dirs = []
        
        for dir_name in common_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                detected_dirs.append(dir_name)
        
        # Suggest based on project type
        suggested_dirs = []
        if project_info['type'] == 'nodejs':
            if project_info['framework'] == 'vite':
                suggested_dirs = ['dist']
            elif project_info['framework'] == 'nextjs':
                suggested_dirs = ['.next', 'out']
            elif project_info['framework'] == 'react':
                suggested_dirs = ['build', 'dist']
            else:
                suggested_dirs = ['dist', 'build']
        elif project_info['type'] == 'python':
            suggested_dirs = ['.', 'static']
        elif project_info['type'] == 'java':
            suggested_dirs = ['target', 'build/libs']
        
        # Combine detected and suggested
        all_suggestions = list(dict.fromkeys(detected_dirs + suggested_dirs))
        
        if detected_dirs:
            print(f"🔍 Found existing directories: {', '.join(detected_dirs)}")
        
        if all_suggestions:
            default_dir = all_suggestions[0]
            user_input = input(f"What directory is your build output? (default: {default_dir}): ").strip()
            return user_input or default_dir
        else:
            user_input = input("What directory is your build output? (comma-separate if multiple): ").strip()
            return user_input or '.'
    
    def _prompt_start_command(self, project_info: Dict[str, str]) -> str:
        """Prompt for start command with intelligent suggestions"""
        print(f"\n🚀 Start Command")
        print("-" * 15)
        
        suggestions = []
        
        if project_info['type'] == 'nodejs':
            # Check package.json for scripts
            package_json = Path("package.json")
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                        scripts = package_data.get('scripts', {})
                        
                        # Prioritize common start scripts
                        for script_name in ['start', 'dev', 'serve', 'preview']:
                            if script_name in scripts:
                                pkg_mgr = project_info.get('package_manager', 'npm')
                                suggestions.append(f"{pkg_mgr} run {script_name}")
                except:
                    pass
            
            # Framework-specific defaults
            if project_info['framework'] == 'vite':
                suggestions.extend(['npm run dev', 'npm run preview'])
            elif project_info['framework'] == 'nextjs':
                suggestions.extend(['npm run start', 'npm run dev'])
            elif project_info['framework'] == 'express':
                suggestions.extend(['npm start', 'node server.js', 'node index.js'])
        
        elif project_info['type'] == 'python':
            if project_info['framework'] == 'django':
                suggestions = ['python manage.py runserver', 'gunicorn myproject.wsgi:application']
            elif project_info['framework'] == 'flask':
                suggestions = ['python app.py', 'flask run', 'gunicorn app:app']
            elif project_info['framework'] == 'fastapi':
                suggestions = ['uvicorn main:app --host 0.0.0.0 --port 8000']
            else:
                suggestions = ['python main.py', 'python app.py']
        
        elif project_info['type'] == 'java':
            if project_info['build_tool'] == 'maven':
                suggestions = ['mvn spring-boot:run', 'java -jar target/*.jar']
            elif project_info['build_tool'] == 'gradle':
                suggestions = ['./gradlew bootRun', 'java -jar build/libs/*.jar']
        
        elif project_info['type'] == 'go':
            suggestions = ['go run main.go', './main']
        
        elif project_info['type'] == 'rust':
            suggestions = ['cargo run', './target/release/app']
        
        # Show suggestions
        if suggestions:
            print("💡 Suggestions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion}")
            
            default_cmd = suggestions[0]
            # Import security modules locally to avoid circular imports
            from core.security import SecurityValidator, safe_input
            user_input = safe_input(f"\nWhat command do you want to use to start the app? (default: {default_cmd}): ").strip()
            # Validate command input for safety
            if user_input and not SecurityValidator.validate_command_input(user_input):
                from core.exceptions import AutomationError
                raise AutomationError(
                    "Command input contains potentially dangerous characters",
                    suggestion="Use only alphanumeric characters, hyphens, underscores, dots, and slashes"
                )
            return user_input or default_cmd
        else:
            from core.security import SecurityValidator, safe_input
            user_input = safe_input("What command do you want to use to start the app?: ").strip()
            # Validate command input for safety
            if user_input and not SecurityValidator.validate_command_input(user_input):
                from core.exceptions import AutomationError
                raise AutomationError(
                    "Command input contains potentially dangerous characters",
                    suggestion="Use only alphanumeric characters, hyphens, underscores, dots, and slashes"
                )
            return user_input
    
    def _prompt_port(self, project_info: Dict[str, str]) -> str:
        """Prompt for port with intelligent detection"""
        print(f"\n🌐 Port Configuration")
        print("-" * 20)
        
        detected_port = self._detect_port(project_info)
        
        if detected_port:
            print(f"🔍 Detected port: {detected_port}")
            user_input = input(f"What port does your server listen on? (default: {detected_port}): ").strip()
            return user_input or str(detected_port)
        else:
            # Framework defaults
            default_ports = {
                'vite': '5173',
                'nextjs': '3000',
                'react': '3000',
                'vue': '8080',
                'angular': '4200',
                'express': '3000',
                'django': '8000',
                'flask': '5000',
                'fastapi': '8000',
            }
            
            default_port = default_ports.get(project_info.get('framework'), '8080')
            user_input = input(f"What port does your server listen on? (default: {default_port}): ").strip()
            return user_input or default_port
    
    def _detect_port(self, project_info: Dict[str, str]) -> Optional[int]:
        """Detect port from configuration files"""
        cwd = Path.cwd()
        
        # Check common config files
        config_files = [
            'vite.config.js', 'vite.config.ts',
            'next.config.js', 'next.config.ts',
            'package.json',
            '.env', '.env.local', '.env.development',
            'nuxt.config.js', 'nuxt.config.ts'
        ]
        
        port_patterns = [
            r'port[\'\":\s]*(\d+)',
            r'PORT[\'\":\s]*[=]*(\d+)',
            r'server[\'\":\s]*{[^}]*port[\'\":\s]*[:\s]*(\d+)',
            r'dev[\'\":\s]*{[^}]*port[\'\":\s]*[:\s]*(\d+)'
        ]
        
        for config_file in config_files:
            file_path = cwd / config_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    for pattern in port_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            return int(matches[0])
                except:
                    continue
        
        return None
    
    def _generate_dockerfile(self, project_info: Dict[str, str], build_dir: str, start_command: str, port: str):
        """Generate Dockerfile based on project type"""
        dockerfile_content = ""
        
        if project_info['type'] == 'nodejs':
            dockerfile_content = self._generate_nodejs_dockerfile(project_info, build_dir, start_command, port)
        elif project_info['type'] == 'python':
            dockerfile_content = self._generate_python_dockerfile(project_info, build_dir, start_command, port)
        elif project_info['type'] == 'java':
            dockerfile_content = self._generate_java_dockerfile(project_info, build_dir, start_command, port)
        elif project_info['type'] == 'go':
            dockerfile_content = self._generate_go_dockerfile(start_command, port)
        elif project_info['type'] == 'rust':
            dockerfile_content = self._generate_rust_dockerfile(start_command, port)
        else:
            dockerfile_content = self._generate_generic_dockerfile(start_command, port)
        
        # Write Dockerfile
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
    
    def _generate_nodejs_dockerfile(self, project_info: Dict[str, str], build_dir: str, start_command: str, port: str) -> str:
        """Generate Node.js specific Dockerfile"""
        pkg_mgr = project_info.get('package_manager', 'npm')
        
        # Use appropriate package manager commands
        if pkg_mgr == 'yarn':
            install_cmd = 'yarn install'
            copy_lock = 'COPY yarn.lock .'
        elif pkg_mgr == 'pnpm':
            install_cmd = 'pnpm install'
            copy_lock = 'COPY pnpm-lock.yaml .'
        else:
            install_cmd = 'npm install'
            copy_lock = 'COPY package-lock.json* .'
        
        return f"""# Node.js Dockerfile generated by Docker Init
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json .
{copy_lock}

# Install dependencies
RUN {install_cmd}

# Copy source code
COPY . .

# Build the application
RUN {pkg_mgr} run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Copy package files for production dependencies
COPY package.json .
{copy_lock}

# Install only production dependencies
RUN {install_cmd} --only=production

# Copy built application
COPY --from=builder /app/{build_dir} ./{build_dir}

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/ || exit 1

# Start the application
CMD {json.dumps(start_command.split())}
"""
    
    def _generate_python_dockerfile(self, project_info: Dict[str, str], build_dir: str, start_command: str, port: str) -> str:
        """Generate Python specific Dockerfile"""
        base_image = "python:3.11-slim"
        
        if project_info['framework'] == 'django':
            additional_deps = "RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*"
        elif project_info['framework'] == 'fastapi':
            additional_deps = ""
        else:
            additional_deps = ""
        
        return f"""# Python Dockerfile generated by Docker Init
FROM {base_image}

WORKDIR /app

# Install system dependencies
{additional_deps}

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/ || exit 1

# Start the application
CMD {json.dumps(start_command.split())}
"""
    
    def _generate_java_dockerfile(self, project_info: Dict[str, str], build_dir: str, start_command: str, port: str) -> str:
        """Generate Java specific Dockerfile"""
        if project_info['build_tool'] == 'maven':
            build_commands = """
COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn clean package -DskipTests
"""
            jar_path = "target/*.jar"
        else:  # gradle
            build_commands = """
COPY build.gradle* gradlew ./
COPY gradle ./gradle
RUN ./gradlew dependencies

COPY src ./src
RUN ./gradlew build -x test
"""
            jar_path = "build/libs/*.jar"
        
        return f"""# Java Dockerfile generated by Docker Init
FROM openjdk:17-jdk-slim AS builder

WORKDIR /app
{build_commands}

# Runtime stage
FROM openjdk:17-jre-slim

WORKDIR /app

# Copy built JAR
COPY --from=builder /app/{jar_path} app.jar

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/actuator/health || exit 1

# Start the application
CMD ["java", "-jar", "app.jar"]
"""
    
    def _generate_go_dockerfile(self, start_command: str, port: str) -> str:
        """Generate Go specific Dockerfile"""
        return f"""# Go Dockerfile generated by Docker Init
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Runtime stage
FROM alpine:latest

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/main .

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD wget --no-verbose --tries=1 --spider http://localhost:{port}/ || exit 1

# Start the application
CMD ["./main"]
"""
    
    def _generate_rust_dockerfile(self, start_command: str, port: str) -> str:
        """Generate Rust specific Dockerfile"""
        return f"""# Rust Dockerfile generated by Docker Init
FROM rust:1.70 AS builder

WORKDIR /app

# Copy manifest files
COPY Cargo.toml Cargo.lock ./

# Copy source code
COPY src ./src

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/target/release/* ./

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/ || exit 1

# Start the application
CMD ["./app"]
"""
    
    def _generate_generic_dockerfile(self, start_command: str, port: str) -> str:
        """Generate generic Dockerfile"""
        return f"""# Generic Dockerfile generated by Docker Init
FROM alpine:latest

WORKDIR /app

# Install basic dependencies
RUN apk add --no-cache curl

# Copy application files
COPY . .

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/ || exit 1

# Start the application
CMD {json.dumps(start_command.split())}
"""
    
    def _generate_dockerignore(self, project_info: Dict[str, str]):
        """Generate appropriate .dockerignore file"""
        common_ignores = [
            ".git",
            ".gitignore",
            "README.md",
            "Dockerfile",
            ".dockerignore",
            ".env",
            ".env.local",
            ".env.*.local"
        ]
        
        type_specific_ignores = {
            'nodejs': [
                "node_modules",
                "npm-debug.log*",
                "yarn-debug.log*", 
                "yarn-error.log*",
                ".npm",
                ".eslintcache",
                ".next",
                "coverage",
                ".nyc_output"
            ],
            'python': [
                "__pycache__",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".Python",
                "env",
                "venv",
                ".venv",
                "pip-log.txt",
                "pip-delete-this-directory.txt",
                ".tox",
                ".coverage",
                ".pytest_cache",
                "htmlcov"
            ],
            'java': [
                "target/",
                "build/",
                "*.class",
                "*.jar",
                "*.war",
                "*.ear",
                ".gradle",
                ".idea",
                "*.iml"
            ],
            'go': [
                "vendor/",
                "*.test",
                "*.out"
            ],
            'rust': [
                "target/",
                "Cargo.lock"
            ]
        }
        
        ignores = common_ignores.copy()
        if project_info['type'] in type_specific_ignores:
            ignores.extend(type_specific_ignores[project_info['type']])
        
        with open('.dockerignore', 'w') as f:
            f.write('\n'.join(ignores))
            f.write('\n')
    
    def _noninteractive_docker(self, operation: str, **kwargs):
        """Non-interactive Docker operations"""
        operations = {
            'init': self._docker_init,
            'build': self._build_image,
            'run': self._run_container,
            'stop': self._stop_container,
            'list': self._list_containers,
            'prune': self._prune_resources
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        
        operations[operation](interactive=False, **kwargs)
    
    def _is_docker_running(self) -> bool:
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_available_images(self) -> list:
        """Get list of available Docker images"""
        try:
            result = subprocess.run(
                ['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'],
                capture_output=True,
                text=True,
                check=True
            )
            images = result.stdout.strip().split('\n')
            # Filter out empty lines and <none>:<none> images
            images = [img for img in images if img and not img.startswith('<none>')]
            return sorted(images)
        except subprocess.CalledProcessError:
            return []
        except Exception:
            return []
    
    def _image_exists(self, image_name: str) -> bool:
        """Check if a Docker image exists"""
        try:
            result = subprocess.run(
                ['docker', 'image', 'inspect', image_name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _build_image(self, interactive: bool = True, **kwargs):
        """Build Docker image"""
        print("\n🔨 BUILD DOCKER IMAGE")
        print("="*70 + "\n")
        
        if interactive:
            # Get image name
            image_name = input("Image name (e.g., myapp:latest): ").strip()
            if not image_name:
                print("❌ Image name cannot be empty")
                return
            
            # Get Dockerfile path
            from core.security import SecurityValidator, safe_input
            from core.exceptions import AutomationError
            dockerfile = safe_input("Dockerfile path (default: ./Dockerfile): ").strip() or 'Dockerfile'
            # Validate path for safety
            if dockerfile and not SecurityValidator.validate_path(dockerfile):
                raise AutomationError(
                    "Dockerfile path contains potentially dangerous elements",
                    suggestion="Use only relative paths within the project directory"
                )
            
            # Get build context
            from core.security import SecurityValidator, safe_input
            from core.exceptions import AutomationError
            context = safe_input("Build context (default: .): ").strip() or '.'
            # Validate path for safety
            if context and not SecurityValidator.validate_path(context):
                raise AutomationError(
                    "Build context path contains potentially dangerous elements",
                    suggestion="Use only relative paths within the project directory"
                )
        else:
            image_name = kwargs.get('image_name')
            dockerfile = kwargs.get('dockerfile', 'Dockerfile')
            context = kwargs.get('context', '.')
            
            if not image_name:
                raise ValueError("image_name is required")
        
        # Check if Dockerfile exists
        dockerfile_path = Path(context) / dockerfile
        if not dockerfile_path.exists():
            print(f"❌ Dockerfile not found: {dockerfile_path}")
            return
        
        # Import security modules locally to avoid circular imports
        from core.security import SecurityValidator
        from core.logging import log_command_execution
        from core.exceptions import AutomationError

        # Build command
        cmd = ['docker', 'build', '-t', image_name, '-f', dockerfile, context]

        # Validate the command elements for security
        for element in cmd:
            if not SecurityValidator.validate_command_input(str(element)):
                raise AutomationError(
                    f"Command contains potentially dangerous element: {element}",
                    suggestion="Use only safe command elements without shell metacharacters"
                )

        print(f"$ {' '.join(cmd)}\n")

        try:
            # Use secure subprocess run with logging
            SecurityValidator.safe_subprocess_run(cmd, check=True)
            log_command_execution('docker build', f"image: {image_name}, dockerfile: {dockerfile}, context: {context}", True)
            print(f"\n✅ Image '{image_name}' built successfully!")
            
            # Offer to run the container after successful build
            if interactive:
                run_now = input(f"\n🚀 Run container from '{image_name}' now? (y/n, default: n): ").strip().lower()
                if run_now in ['y', 'yes']:
                    print("\n" + "="*70)
                    # Pass the image name to run container function
                    self._run_container_with_image(image_name)
                    
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Build failed with exit code {e.returncode}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _run_container(self, interactive: bool = True, **kwargs):
        """Run Docker container"""
        print("\n▶️  RUN DOCKER CONTAINER")
        print("="*70 + "\n")
        
        if interactive:
            # Get available images
            available_images = self._get_available_images()
            
            if not available_images:
                print("❌ No Docker images available")
                print("💡 Build an image first using option 1")
                return
            
            # Display available images with arrow navigation
            image_options = available_images + ["Enter custom image name"]
            choice = get_choice_with_arrows(image_options, "Available Images")
            
            if 1 <= choice <= len(available_images):
                image_name = available_images[choice - 1]
            elif choice == len(available_images) + 1:
                image_name = input("Enter image name: ").strip()
                if not image_name:
                    print("❌ Image name cannot be empty")
                    return
            else:
                print("❌ Invalid choice")
                return
            
            # Verify image exists
            if not self._image_exists(image_name):
                print(f"❌ Image '{image_name}' not found")
                print("💡 Available images are listed above")
                return
            
            # Get container name
            container_name = input("Container name (optional): ").strip()
            
            # Port mapping
            port_map = input("Port mapping (e.g., 8080:80, optional): ").strip()
            
            # Environment variables
            env_vars = input("Environment variables (e.g., ENV1=value1,ENV2=value2, optional): ").strip()
            
            # Volume mapping
            volume_map = input("Volume mapping (e.g., /host/path:/container/path, optional): ").strip()
            
            # Run mode with arrow navigation
            mode_options = ["Detached (background)", "Interactive (foreground)"]
            mode_choice = get_choice_with_arrows(mode_options, "Run mode")
            detached = (mode_choice == 1)
        else:
            image_name = kwargs.get('image_name')
            container_name = kwargs.get('container_name', '')
            port_map = kwargs.get('port_map', '')
            env_vars = kwargs.get('env_vars', '')
            volume_map = kwargs.get('volume_map', '')
            detached = kwargs.get('detached', True)
            
            if not image_name:
                raise ValueError("image_name is required")
        
        # Build command
        cmd = ['docker', 'run']
        
        if detached:
            cmd.append('-d')
        else:
            cmd.extend(['-it'])
        
        if container_name:
            cmd.extend(['--name', container_name])
        
        if port_map:
            cmd.extend(['-p', port_map])
        
        if volume_map:
            cmd.extend(['-v', volume_map])
        
        # Add environment variables
        if env_vars:
            for env_var in env_vars.split(','):
                env_var = env_var.strip()
                if '=' in env_var:
                    cmd.extend(['-e', env_var])
        
        cmd.append(image_name)
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if detached:
                container_id = result.stdout.strip()[:12]
                print(f"✅ Container started: {container_id}")
                if container_name:
                    print(f"📝 Container name: {container_name}")
                if port_map:
                    host_port = port_map.split(':')[0]
                    print(f"🌐 Access at: http://localhost:{host_port}")
                print(f"🔍 View logs: docker logs {container_id}")
            else:
                print("✅ Container stopped")
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to run container:")
            print(f"   Exit code: {e.returncode}")
            if e.stderr:
                print(f"   Error: {e.stderr.strip()}")
            if e.stdout:
                print(f"   Output: {e.stdout.strip()}")
            
            # Common error suggestions
            if e.returncode == 125:
                print("\n💡 Common solutions for exit code 125:")
                print("   • Check if the image name is correct")
                print("   • Verify the image exists: docker images")
                print("   • Check if port is already in use")
                print("   • Ensure container name is unique")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _run_container_with_image(self, image_name: str):
        """Run container with pre-selected image"""
        print(f"▶️  RUN CONTAINER: {image_name}")
        print("="*70 + "\n")
        
        # Get container name
        container_name = input("Container name (optional): ").strip()
        
        # Port mapping
        port_map = input("Port mapping (e.g., 8080:80, optional): ").strip()
        
        # Environment variables
        env_vars = input("Environment variables (e.g., ENV1=value1,ENV2=value2, optional): ").strip()
        
        # Volume mapping
        volume_map = input("Volume mapping (e.g., /host/path:/container/path, optional): ").strip()
        
        # Run mode with arrow navigation
        mode_options = ["Detached (background)", "Interactive (foreground)"]
        mode_choice = get_choice_with_arrows(mode_options, "Run mode")
        detached = (mode_choice == 1)
        
        # Build command
        cmd = ['docker', 'run']
        
        if detached:
            cmd.append('-d')
        else:
            cmd.extend(['-it'])
        
        if container_name:
            cmd.extend(['--name', container_name])
        
        if port_map:
            cmd.extend(['-p', port_map])
        
        if volume_map:
            cmd.extend(['-v', volume_map])
        
        # Add environment variables
        if env_vars:
            for env_var in env_vars.split(','):
                env_var = env_var.strip()
                if '=' in env_var:
                    cmd.extend(['-e', env_var])
        
        cmd.append(image_name)
        
        print(f"\n$ {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if detached:
                container_id = result.stdout.strip()[:12]
                print(f"✅ Container started: {container_id}")
                if container_name:
                    print(f"📝 Container name: {container_name}")
                if port_map:
                    host_port = port_map.split(':')[0]
                    print(f"🌐 Access at: http://localhost:{host_port}")
                print(f"🔍 View logs: docker logs {container_id}")
            else:
                print("✅ Container stopped")
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to run container:")
            print(f"   Exit code: {e.returncode}")
            if e.stderr:
                print(f"   Error: {e.stderr.strip()}")
            if e.stdout:
                print(f"   Output: {e.stdout.strip()}")
            
            # Common error suggestions
            if e.returncode == 125:
                print("\n💡 Common solutions for exit code 125:")
                print("   • Check if the image name is correct")
                print("   • Verify the image exists: docker images")
                print("   • Check if port is already in use")
                print("   • Ensure container name is unique")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _stop_container(self, interactive: bool = True, **kwargs):
        """Stop Docker container"""
        print("\n🛑 STOP DOCKER CONTAINER")
        print("="*70 + "\n")
        
        # List running containers
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            containers = result.stdout.strip().split('\n')
            containers = [c for c in containers if c]
            
            if not containers:
                print("ℹ️  No running containers")
                return
            
            if interactive:
                # Prepare container options for arrow navigation
                container_options = []
                for container in containers:
                    parts = container.split('\t')
                    container_id = parts[0][:12]  # Short ID
                    name = parts[1] if len(parts) > 1 else '<none>'
                    image = parts[2] if len(parts) > 2 else '<unknown>'
                    status = parts[3] if len(parts) > 3 else '<unknown>'
                    container_options.append(f"{container_id} | {name} | {image} | {status}")
                
                container_options.append("Stop All")
                
                choice = get_choice_with_arrows(container_options, "Running Containers")
                
                if 1 <= choice <= len(containers):
                    container_info = containers[choice - 1].split('\t')
                    container_id = container_info[0]
                elif choice == len(containers) + 1:
                    # Stop all containers
                    self._stop_all_containers()
                    return
                else:
                    print("❌ Invalid choice")
                    return
            else:
                container_id = kwargs.get('container_id')
                if not container_id:
                    raise ValueError("container_id is required")
            
            # Stop container
            cmd = ['docker', 'stop', container_id]
            print(f"\n$ {' '.join(cmd)}\n")
            
            subprocess.run(cmd, check=True)
            print(f"✅ Container {container_id} stopped")
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to stop container: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _stop_all_containers(self):
        """Stop all running containers"""
        try:
            # Get all running container IDs
            result = subprocess.run(
                ['docker', 'ps', '-q'],
                capture_output=True,
                text=True,
                check=True
            )
            
            container_ids = result.stdout.strip().split('\n')
            container_ids = [cid for cid in container_ids if cid]
            
            if not container_ids:
                print("ℹ️  No running containers to stop")
                return
            
            print(f"🛑 Stopping {len(container_ids)} container(s)...")
            
            # Stop all containers
            cmd = ['docker', 'stop'] + container_ids
            print(f"$ {' '.join(cmd[:3])} [...]")
            
            subprocess.run(cmd, check=True)
            print(f"✅ All containers stopped successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to stop all containers: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _list_containers(self, interactive: bool = True, all_containers: bool = False):
        """List Docker containers"""
        print("\n📋 DOCKER CONTAINERS")
        print("="*70 + "\n")
        
        cmd = ['docker', 'ps']
        if all_containers:
            cmd.append('-a')
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to list containers: {e}")
    
    def _list_images(self):
        """List Docker images"""
        print("\n📋 DOCKER IMAGES")
        print("="*70 + "\n")
        
        try:
            subprocess.run(['docker', 'images'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to list images: {e}")
    
    def _prune_resources(self, interactive: bool = True):
        """Prune unused Docker resources"""
        print("\n🧹 PRUNE UNUSED RESOURCES")
        print("="*70 + "\n")
        
        print("⚠️  This will remove:")
        print("  • All stopped containers")
        print("  • All unused networks")
        print("  • All dangling images")
        print("  • All build cache")
        
        if interactive:
            confirm = input("\nProceed? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Operation cancelled")
                return
        
        print("\n🔨 Pruning resources...\n")
        
        try:
            subprocess.run(['docker', 'system', 'prune', '-f'], check=True)
            print("\n✅ Resources pruned successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Prune failed: {e}")
    
    def _docker_compose_menu(self):
        """Docker Compose operations menu"""
        print("\n" + "="*70)
        print("🐳 DOCKER COMPOSE INTEGRATION")
        print("="*70 + "\n")
        
        # Check if docker-compose is installed
        if not self.validate_binary('docker-compose'):
            self.show_missing_binary_error(
                'docker-compose',
                'https://docs.docker.com/compose/install/'
            )
            input("\nPress Enter to continue...")
            return
        
        # Docker Compose operations menu
        compose_options = [
            "Initialize docker-compose.yml",
            "Start Services (up)",
            "Stop Services (down)",
            "Restart Services",
            "View Service Logs",
            "List Services",
            "Scale Services",
            "Build Services",
            "Pull Services",
            "Remove Stopped Containers",
            "Back to Main Menu"
        ]
        
        choice = get_choice_with_arrows(compose_options, "Docker Compose Operations")
        
        if choice == 1:
            self._docker_compose_init()
        elif choice == 2:
            self._docker_compose_up()
        elif choice == 3:
            self._docker_compose_down()
        elif choice == 4:
            self._docker_compose_restart()
        elif choice == 5:
            self._docker_compose_logs()
        elif choice == 6:
            self._docker_compose_ps()
        elif choice == 7:
            self._docker_compose_scale()
        elif choice == 8:
            self._docker_compose_build()
        elif choice == 9:
            self._docker_compose_pull()
        elif choice == 10:
            self._docker_compose_rm()
        elif choice == 11:
            return
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")
    
    def _docker_compose_init(self):
        """Initialize docker-compose.yml with intelligent service detection"""
        print("\n📝 DOCKER COMPOSE INITIALIZATION")
        print("="*70 + "\n")
        
        # Detect project type and existing Dockerfile
        project_info = self._detect_project_type()
        dockerfile_exists = Path("Dockerfile").exists()
        compose_file_exists = Path("docker-compose.yml").exists() or Path("docker-compose.yaml").exists()
        
        print(f"📋 Detected project type: {project_info['type']}")
        if project_info['framework']:
            print(f"🔧 Framework: {project_info['framework']}")
        print(f"🐳 Dockerfile exists: {'Yes' if dockerfile_exists else 'No'}")
        print(f"📄 Compose file exists: {'Yes' if compose_file_exists else 'No'}")
        print()
        
        if compose_file_exists:
            overwrite = input("docker-compose.yml already exists. Overwrite? (y/n, default: n): ").strip().lower()
            if overwrite not in ['y', 'yes']:
                print("❌ Operation cancelled")
                return
        
        # Get service configuration
        app_name = input("Application service name (default: app): ").strip() or "app"
        app_port = input("Application port (default: 3000): ").strip() or "3000"
        
        # Ask about additional services
        print("\n🔧 ADDITIONAL SERVICES")
        print("-" * 25)
        
        services = {}
        
        # Database options
        db_choice = input("Add database service? (postgres/mysql/mongo/redis/no, default: no): ").strip().lower()
        if db_choice in ['postgres', 'postgresql']:
            services['database'] = {
                'image': 'postgres:15',
                'env': ['POSTGRES_DB=appdb', 'POSTGRES_USER=appuser', 'POSTGRES_PASSWORD=apppass'],
                'volumes': ['postgres_data:/var/lib/postgresql/data'],
                'ports': ['5432:5432']
            }
        elif db_choice == 'mysql':
            services['database'] = {
                'image': 'mysql:8',
                'env': ['MYSQL_DATABASE=appdb', 'MYSQL_USER=appuser', 'MYSQL_PASSWORD=apppass', 'MYSQL_ROOT_PASSWORD=rootpass'],
                'volumes': ['mysql_data:/var/lib/mysql'],
                'ports': ['3306:3306']
            }
        elif db_choice == 'mongo' or db_choice == 'mongodb':
            services['database'] = {
                'image': 'mongo:6',
                'env': ['MONGO_INITDB_ROOT_USERNAME=admin', 'MONGO_INITDB_ROOT_PASSWORD=apppass'],
                'volumes': ['mongo_data:/data/db'],
                'ports': ['27017:27017']
            }
        elif db_choice == 'redis':
            services['redis'] = {
                'image': 'redis:7-alpine',
                'volumes': ['redis_data:/data'],
                'ports': ['6379:6379']
            }
        
        # Nginx reverse proxy
        nginx_choice = input("Add Nginx reverse proxy? (y/n, default: n): ").strip().lower()
        if nginx_choice in ['y', 'yes']:
            services['nginx'] = {
                'image': 'nginx:alpine',
                'volumes': ['./nginx.conf:/etc/nginx/nginx.conf'],
                'ports': ['80:80', '443:443'],
                'depends_on': [app_name]
            }
        
        # Generate docker-compose.yml
        compose_content = self._generate_docker_compose(project_info, app_name, app_port, services)
        
        # Write docker-compose.yml
        compose_file = Path("docker-compose.yml")
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        print(f"\n✅ docker-compose.yml created successfully!")
        
        # Generate .env file if services have environment variables
        if services:
            self._generate_env_file(services)
        
        # Generate nginx.conf if nginx was added
        if 'nginx' in services:
            self._generate_nginx_conf(app_name, app_port)
        
        print(f"\n🎉 Docker Compose initialization complete!")
        print(f"📄 Services configured: {len(services) + 1}")
        print(f"🚀 Start with: docker-compose up -d")
    
    def _generate_docker_compose(self, project_info: Dict[str, str], app_name: str, app_port: str, services: Dict) -> str:
        """Generate docker-compose.yml content"""
        
        # Main application service
        app_service = f"""  {app_name}:
    build: .
    ports:
      - "{app_port}:{app_port}"
    environment:
      - NODE_ENV=development"""
        
        # Add environment variables based on services
        if 'database' in services:
            db_type = services['database']['image'].split(':')[0]
            if db_type == 'postgres':
                app_service += f"""
      - DATABASE_URL=postgresql://appuser:apppass@database:5432/appdb"""
            elif db_type == 'mysql':
                app_service += f"""
      - DATABASE_URL=mysql://appuser:apppass@database:3306/appdb"""
            elif db_type == 'mongo':
                app_service += f"""
      - DATABASE_URL=mongodb://admin:apppass@database:27017/appdb"""
        
        if 'redis' in services:
            app_service += f"""
      - REDIS_URL=redis://redis:6379"""
        
        # Add volumes for development
        app_service += f"""
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:"""
        
        # Add dependencies
        if 'database' in services:
            app_service += f"""
      - database"""
        if 'redis' in services:
            app_service += f"""
      - redis"""
        
        # Start building the compose file
        compose_content = f"""version: '3.8'

services:
{app_service}
"""
        
        # Add additional services
        for service_name, service_config in services.items():
            compose_content += f"\n  {service_name}:\n"
            compose_content += f"    image: {service_config['image']}\n"
            
            if 'ports' in service_config:
                compose_content += "    ports:\n"
                for port in service_config['ports']:
                    compose_content += f"      - \"{port}\"\n"
            
            if 'env' in service_config:
                compose_content += "    environment:\n"
                for env_var in service_config['env']:
                    compose_content += f"      - {env_var}\n"
            
            if 'volumes' in service_config:
                compose_content += "    volumes:\n"
                for volume in service_config['volumes']:
                    compose_content += f"      - {volume}\n"
            
            if 'depends_on' in service_config:
                compose_content += "    depends_on:\n"
                for dep in service_config['depends_on']:
                    compose_content += f"      - {dep}\n"
            
            # Add restart policy for services
            if service_name != app_name:
                compose_content += "    restart: unless-stopped\n"
        
        # Add volumes section
        compose_content += "\nvolumes:\n"
        for service_name, service_config in services.items():
            if 'volumes' in service_config:
                for volume in service_config['volumes']:
                    if ':' not in volume:  # Named volume
                        compose_content += f"  {volume}:\n"
        
        # Add networks section for better isolation
        compose_content += """
networks:
  default:
    driver: bridge"""
        
        return compose_content
    
    def _generate_env_file(self, services: Dict):
        """Generate .env file for environment variables"""
        env_content = "# Environment variables for Docker Compose\n"
        
        for service_name, service_config in services.items():
            if 'env' in service_config:
                env_content += f"\n# {service_name.title()} variables\n"
                for env_var in service_config['env']:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        env_content += f"{key}={value}\n"
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
    
    def _generate_nginx_conf(self, app_name: str, app_port: str):
        """Generate nginx.conf for reverse proxy"""
        nginx_content = f"""events {{
    worker_connections 1024;
}}

http {{
    upstream app {{
        server {app_name}:{app_port};
    }}
    
    server {{
        listen 80;
        server_name localhost;
        
        location / {{
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
    }}
}}"""
        
        with open('nginx.conf', 'w') as f:
            f.write(nginx_content)
        
        print("✅ nginx.conf created successfully!")
    
    def _docker_compose_up(self):
        """Start Docker Compose services"""
        print("\n🚀 DOCKER COMPOSE UP")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            print("💡 Run 'Initialize docker-compose.yml' first")
            return
        
        detached = input("Run in detached mode? (Y/n, default: Y): ").strip().lower()
        detached = detached not in ['n', 'no']
        
        cmd = ['docker-compose', 'up']
        if detached:
            cmd.append('-d')
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            if detached:
                print("✅ Services started successfully!")
                self._docker_compose_ps(show_output=False)
            else:
                print("✅ Services stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e}")
    
    def _docker_compose_down(self):
        """Stop Docker Compose services"""
        print("\n🛑 DOCKER COMPOSE DOWN")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        remove_volumes = input("Remove volumes? (y/N, default: N): ").strip().lower()
        remove_volumes = remove_volumes in ['y', 'yes']
        
        cmd = ['docker-compose', 'down']
        if remove_volumes:
            cmd.append('-v')
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Services stopped successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop services: {e}")
    
    def _docker_compose_restart(self):
        """Restart Docker Compose services"""
        print("\n🔄 DOCKER COMPOSE RESTART")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        cmd = ['docker-compose', 'restart']
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Services restarted successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restart services: {e}")
    
    def _docker_compose_logs(self):
        """View Docker Compose service logs"""
        print("\n📋 DOCKER COMPOSE LOGS")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        follow = input("Follow logs? (Y/n, default: Y): ").strip().lower()
        follow = follow not in ['n', 'no']
        
        service = input("Specific service? (leave empty for all): ").strip()
        
        cmd = ['docker-compose', 'logs']
        if follow:
            cmd.append('-f')
        if service:
            cmd.append(service)
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to view logs: {e}")
        except KeyboardInterrupt:
            print("\n📋 Logs viewing stopped")
    
    def _docker_compose_ps(self, show_output: bool = True):
        """List Docker Compose services"""
        if show_output:
            print("\n📋 DOCKER COMPOSE SERVICES")
            print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            if show_output:
                print("❌ docker-compose.yml not found")
            return
        
        cmd = ['docker-compose', 'ps']
        
        if show_output:
            print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if show_output:
                print(f"❌ Failed to list services: {e}")
    
    def _docker_compose_scale(self):
        """Scale Docker Compose services"""
        print("\n📈 DOCKER COMPOSE SCALE")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        service = input("Service name to scale: ").strip()
        if not service:
            print("❌ Service name cannot be empty")
            return
        
        replicas = input("Number of replicas: ").strip()
        if not replicas.isdigit() or int(replicas) < 1:
            print("❌ Invalid number of replicas")
            return
        
        cmd = ['docker-compose', 'up', '-d', '--scale', f'{service}={replicas}']
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Service '{service}' scaled to {replicas} replicas!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to scale service: {e}")
    
    def _docker_compose_build(self):
        """Build Docker Compose services"""
        print("\n🔨 DOCKER COMPOSE BUILD")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        no_cache = input("Build without cache? (y/N, default: N): ").strip().lower()
        no_cache = no_cache in ['y', 'yes']
        
        service = input("Specific service? (leave empty for all): ").strip()
        
        cmd = ['docker-compose', 'build']
        if no_cache:
            cmd.append('--no-cache')
        if service:
            cmd.append(service)
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Services built successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build services: {e}")
    
    def _docker_compose_pull(self):
        """Pull Docker Compose service images"""
        print("\n📥 DOCKER COMPOSE PULL")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        service = input("Specific service? (leave empty for all): ").strip()
        
        cmd = ['docker-compose', 'pull']
        if service:
            cmd.append(service)
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Images pulled successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to pull images: {e}")
    
    def _docker_compose_rm(self):
        """Remove stopped Docker Compose containers"""
        print("\n🗑️  DOCKER COMPOSE REMOVE")
        print("="*70 + "\n")
        
        if not Path("docker-compose.yml").exists() and not Path("docker-compose.yaml").exists():
            print("❌ docker-compose.yml not found")
            return
        
        force = input("Force removal? (y/N, default: N): ").strip().lower()
        force = force in ['y', 'yes']
        
        cmd = ['docker-compose', 'rm']
        if force:
            cmd.append('-f')
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Stopped containers removed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove containers: {e}")
    
    def _container_orchestration_menu(self):
        """Container Orchestration (Docker Swarm) menu"""
        print("\n" + "="*70)
        print("🐳 CONTAINER ORCHESTRATION (DOCKER SWARM)")
        print("="*70 + "\n")
        
        # Check if Docker is running
        if not self._is_docker_running():
            print("❌ Docker daemon is not running")
            input("\nPress Enter to continue...")
            return
        
        # Check if Swarm is initialized
        swarm_status = self._get_swarm_status()
        
        # Swarm operations menu
        swarm_options = [
            "Initialize Swarm",
            "Join Swarm",
            "Leave Swarm",
            "Deploy Stack",
            "List Services",
            "List Nodes",
            "Scale Service",
            "Update Service",
            "Remove Service",
            "List Stacks",
            "Remove Stack",
            "Swarm Status",
            "Back to Main Menu"
        ]
        
        choice = get_choice_with_arrows(swarm_options, "Docker Swarm Operations")
        
        if choice == 1:
            self._swarm_init()
        elif choice == 2:
            self._swarm_join()
        elif choice == 3:
            self._swarm_leave()
        elif choice == 4:
            self._swarm_deploy()
        elif choice == 5:
            self._swarm_list_services()
        elif choice == 6:
            self._swarm_list_nodes()
        elif choice == 7:
            self._swarm_scale_service()
        elif choice == 8:
            self._swarm_update_service()
        elif choice == 9:
            self._swarm_remove_service()
        elif choice == 10:
            self._swarm_list_stacks()
        elif choice == 11:
            self._swarm_remove_stack()
        elif choice == 12:
            self._swarm_status()
        elif choice == 13:
            return
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")
    
    def _get_swarm_status(self) -> Dict[str, str]:
        """Get Docker Swarm status"""
        try:
            result = subprocess.run(
                ['docker', 'info', '--format', '{{.Swarm.LocalNodeState}}'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            state = result.stdout.strip()
            
            if state == 'active':
                # Get more details
                info_result = subprocess.run(
                    ['docker', 'info', '--format', '{{.Swarm.NodeID}} {{.Swarm.NodeAddr}}'],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10
                )
                node_info = info_result.stdout.strip().split()
                
                return {
                    'state': 'active',
                    'node_id': node_info[0] if len(node_info) > 0 else 'unknown',
                    'node_addr': node_info[1] if len(node_info) > 1 else 'unknown'
                }
            else:
                return {'state': state}
                
        except subprocess.CalledProcessError:
            return {'state': 'unknown'}
        except Exception:
            return {'state': 'error'}
    
    def _swarm_init(self):
        """Initialize Docker Swarm"""
        print("\n🚀 DOCKER SWARM INITIALIZATION")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] == 'active':
            print("ℹ️  This node is already part of a Swarm")
            print(f"   Node ID: {swarm_status.get('node_id', 'unknown')}")
            print(f"   Address: {swarm_status.get('node_addr', 'unknown')}")
            
            reset = input("Reset and reinitialize? (y/N, default: N): ").strip().lower()
            if reset not in ['y', 'yes']:
                return
            
            # Leave current swarm first
            try:
                subprocess.run(['docker', 'swarm', 'leave', '-f'], check=True)
                print("✅ Left current Swarm")
            except subprocess.CalledProcessError:
                print("⚠️  Could not leave current Swarm")
        
        # Get advertise address
        advertise_addr = input("Advertise address (default: auto-detect): ").strip()
        
        # Get listen address
        listen_addr = input("Listen address (default: 0.0.0.0:2377): ").strip() or "0.0.0.0:2377"
        
        cmd = ['docker', 'swarm', 'init']
        
        if advertise_addr:
            cmd.extend(['--advertise-addr', advertise_addr])
        
        if listen_addr != "0.0.0.0:2377":
            cmd.extend(['--listen-addr', listen_addr])
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Swarm initialized successfully!")
            
            # Show join token for workers
            if result.stdout:
                print("\n📋 To add worker nodes, run:")
                print(result.stdout.strip())
            
            # Get manager join token
            try:
                token_result = subprocess.run(
                    ['docker', 'swarm', 'join-token', 'manager'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if token_result.stdout:
                    print("\n📋 To add manager nodes, run:")
                    print(token_result.stdout.strip())
            except:
                pass
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to initialize Swarm: {e}")
    
    def _swarm_join(self):
        """Join existing Docker Swarm"""
        print("\n🔗 DOCKER SWARM JOIN")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] == 'active':
            print("❌ This node is already part of a Swarm")
            return
        
        # Get join token
        join_token = input("Join token: ").strip()
        if not join_token:
            print("❌ Join token cannot be empty")
            return
        
        # Get manager address
        manager_addr = input("Manager address (IP:PORT): ").strip()
        if not manager_addr:
            print("❌ Manager address cannot be empty")
            return
        
        # Ask if joining as worker or manager
        role = input("Join as worker or manager? (worker/manager, default: worker): ").strip().lower()
        if role not in ['worker', 'manager']:
            role = 'worker'
        
        # Listen address
        listen_addr = input("Listen address (default: 0.0.0.0:2377): ").strip() or "0.0.0.0:2377"
        
        cmd = ['docker', 'swarm', 'join', '--token', join_token]
        
        if role == 'manager':
            cmd.append('--manager')
        
        cmd.extend([manager_addr])
        
        if listen_addr != "0.0.0.0:2377":
            cmd.extend(['--listen-addr', listen_addr])
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Successfully joined Swarm as {role}!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to join Swarm: {e}")
    
    def _swarm_leave(self):
        """Leave Docker Swarm"""
        print("\n👋 DOCKER SWARM LEAVE")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        force = input("Force leave? (y/N, default: N): ").strip().lower()
        force = force in ['y', 'yes']
        
        cmd = ['docker', 'swarm', 'leave']
        if force:
            cmd.append('-f')
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Successfully left Swarm!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to leave Swarm: {e}")
    
    def _swarm_deploy(self):
        """Deploy stack to Docker Swarm"""
        print("\n🚀 DOCKER SWARM DEPLOY")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        # Check for compose file
        compose_file = None
        if Path("docker-compose.yml").exists():
            compose_file = "docker-compose.yml"
        elif Path("docker-compose.yaml").exists():
            compose_file = "docker-compose.yaml"
        elif Path("docker-stack.yml").exists():
            compose_file = "docker-stack.yml"
        elif Path("docker-stack.yaml").exists():
            compose_file = "docker-stack.yaml"
        
        if not compose_file:
            print("❌ No Docker Compose file found")
            print("💡 Expected files: docker-compose.yml, docker-compose.yaml, docker-stack.yml, docker-stack.yaml")
            return
        
        stack_name = input("Stack name: ").strip()
        if not stack_name:
            print("❌ Stack name cannot be empty")
            return
        
        cmd = ['docker', 'stack', 'deploy', '-c', compose_file, stack_name]
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Stack '{stack_name}' deployed successfully!")
            
            # Show services
            print("\n📋 Deployed services:")
            self._swarm_list_services(stack_name, show_output=False)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy stack: {e}")
    
    def _swarm_list_services(self, stack_name: str = None, show_output: bool = True):
        """List Swarm services"""
        if show_output:
            print("\n📋 SWARM SERVICES")
            print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            if show_output:
                print("❌ This node is not part of a Swarm")
            return
        
        cmd = ['docker', 'service', 'ls', '--format', 'table {{.ID}}\t{{.Name}}\t{{.Mode}}\t{{.Replicas}}\t{{.Image}}\t{{.Ports}}']
        
        if show_output:
            print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if show_output:
                print(f"❌ Failed to list services: {e}")
    
    def _swarm_list_nodes(self):
        """List Swarm nodes"""
        print("\n📋 SWARM NODES")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        cmd = ['docker', 'node', 'ls', '--format', 'table {{.ID}}\t{{.Hostname}}\t{{.Status}}\t{{.Availability}}\t{{.ManagerStatus}}']
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list nodes: {e}")
    
    def _swarm_scale_service(self):
        """Scale Swarm service"""
        print("\n📈 SWARM SCALE SERVICE")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        # Get available services
        try:
            result = subprocess.run(
                ['docker', 'service', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                check=True
            )
            services = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            
            if not services:
                print("❌ No services found")
                return
            
            print("📋 Available services:")
            for i, service in enumerate(services, 1):
                print(f"   {i}. {service}")
            
            choice = input(f"\nSelect service (1-{len(services)}): ").strip()
            
            try:
                service_idx = int(choice) - 1
                if 0 <= service_idx < len(services):
                    service_name = services[service_idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
                
        except subprocess.CalledProcessError:
            print("❌ Failed to get services list")
            return
        
        replicas = input("Number of replicas: ").strip()
        if not replicas.isdigit() or int(replicas) < 0:
            print("❌ Invalid number of replicas")
            return
        
        cmd = ['docker', 'service', 'scale', f'{service_name}={replicas}']
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Service '{service_name}' scaled to {replicas} replicas!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to scale service: {e}")
    
    def _swarm_update_service(self):
        """Update Swarm service"""
        print("\n🔄 SWARM UPDATE SERVICE")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        # Get available services
        try:
            result = subprocess.run(
                ['docker', 'service', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                check=True
            )
            services = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            
            if not services:
                print("❌ No services found")
                return
            
            print("📋 Available services:")
            for i, service in enumerate(services, 1):
                print(f"   {i}. {service}")
            
            choice = input(f"\nSelect service (1-{len(services)}): ").strip()
            
            try:
                service_idx = int(choice) - 1
                if 0 <= service_idx < len(services):
                    service_name = services[service_idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
                
        except subprocess.CalledProcessError:
            print("❌ Failed to get services list")
            return
        
        # Update options
        print("\n🔧 Update Options:")
        print("1. Update image")
        print("2. Add/remove environment variables")
        print("3. Update replicas")
        print("4. Update placement constraints")
        print("5. Force update")
        
        update_choice = input("Select update option (1-5): ").strip()
        
        cmd = ['docker', 'service', 'update', service_name]
        
        if update_choice == '1':
            new_image = input("New image: ").strip()
            if new_image:
                cmd.extend(['--image', new_image])
        elif update_choice == '2':
            env_vars = input("Environment variables (KEY=VALUE, comma-separated): ").strip()
            if env_vars:
                for env_var in env_vars.split(','):
                    env_var = env_var.strip()
                    if '=' in env_var:
                        cmd.extend(['--env-add', env_var])
        elif update_choice == '3':
            replicas = input("Number of replicas: ").strip()
            if replicas.isdigit():
                cmd.extend(['--replicas', replicas])
        elif update_choice == '4':
            constraints = input("Placement constraints (comma-separated): ").strip()
            if constraints:
                for constraint in constraints.split(','):
                    constraint = constraint.strip()
                    cmd.extend(['--constraint', constraint])
        elif update_choice == '5':
            cmd.append('--force')
        else:
            print("❌ Invalid option")
            return
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Service '{service_name}' updated successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update service: {e}")
    
    def _swarm_remove_service(self):
        """Remove Swarm service"""
        print("\n🗑️  SWARM REMOVE SERVICE")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        # Get available services
        try:
            result = subprocess.run(
                ['docker', 'service', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                check=True
            )
            services = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            
            if not services:
                print("❌ No services found")
                return
            
            print("📋 Available services:")
            for i, service in enumerate(services, 1):
                print(f"   {i}. {service}")
            
            choice = input(f"\nSelect service to remove (1-{len(services)}): ").strip()
            
            try:
                service_idx = int(choice) - 1
                if 0 <= service_idx < len(services):
                    service_name = services[service_idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
                
        except subprocess.CalledProcessError:
            print("❌ Failed to get services list")
            return
        
        confirm = input(f"Remove service '{service_name}'? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Operation cancelled")
            return
        
        cmd = ['docker', 'service', 'rm', service_name]
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Service '{service_name}' removed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove service: {e}")
    
    def _swarm_list_stacks(self):
        """List Swarm stacks"""
        print("\n📋 SWARM STACKS")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        cmd = ['docker', 'stack', 'ls', '--format', 'table {{.Name}}\t{{.Services}}']
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to list stacks: {e}")
    
    def _swarm_remove_stack(self):
        """Remove Swarm stack"""
        print("\n🗑️  SWARM REMOVE STACK")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        if swarm_status['state'] != 'active':
            print("❌ This node is not part of a Swarm")
            return
        
        # Get available stacks
        try:
            result = subprocess.run(
                ['docker', 'stack', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                check=True
            )
            stacks = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            
            if not stacks:
                print("❌ No stacks found")
                return
            
            print("📋 Available stacks:")
            for i, stack in enumerate(stacks, 1):
                print(f"   {i}. {stack}")
            
            choice = input(f"\nSelect stack to remove (1-{len(stacks)}): ").strip()
            
            try:
                stack_idx = int(choice) - 1
                if 0 <= stack_idx < len(stacks):
                    stack_name = stacks[stack_idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
                
        except subprocess.CalledProcessError:
            print("❌ Failed to get stacks list")
            return
        
        confirm = input(f"Remove stack '{stack_name}' and all its services? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Operation cancelled")
            return
        
        cmd = ['docker', 'stack', 'rm', stack_name]
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Stack '{stack_name}' removed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove stack: {e}")
    
    def _swarm_status(self):
        """Show detailed Swarm status"""
        print("\n📊 SWARM STATUS")
        print("="*70 + "\n")
        
        swarm_status = self._get_swarm_status()
        
        print(f"🔸 Swarm State: {swarm_status['state']}")
        
        if swarm_status['state'] == 'active':
            print(f"🔸 Node ID: {swarm_status.get('node_id', 'unknown')}")
            print(f"🔸 Node Address: {swarm_status.get('node_addr', 'unknown')}")
            
            # Show nodes
            print("\n📋 Nodes:")
            try:
                subprocess.run(['docker', 'node', 'ls'], check=True)
            except subprocess.CalledProcessError:
                print("   Could not retrieve node list")
            
            # Show services
            print("\n📋 Services:")
            try:
                subprocess.run(['docker', 'service', 'ls'], check=True)
            except subprocess.CalledProcessError:
                print("   Could not retrieve service list")
            
            # Show stacks
            print("\n📋 Stacks:")
            try:
                subprocess.run(['docker', 'stack', 'ls'], check=True)
            except subprocess.CalledProcessError:
                print("   Could not retrieve stack list")
        else:
            print("💡 To initialize a Swarm, run 'Initialize Swarm' from the menu")


# Export command instance
COMMAND = DockerQuickCommand()