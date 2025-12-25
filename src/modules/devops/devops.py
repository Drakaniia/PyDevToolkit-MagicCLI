"""
DevOps Module
Handles infrastructure as code, container management, deployment automation, and environment management
"""
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator
class DevOpsTools:
    """Handles DevOps and infrastructure tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def setup_terraform_config(self) -> None:
        """Help set up Terraform configuration"""
        print("\n" + "="*70)
        print("TERRAFORM CONFIGURATION SETUP")
        print("="*70)

        print("\nThis tool helps set up Terraform for infrastructure as code.")

        # Check if Terraform is installed
        result = subprocess.run(['terraform', 'version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ Terraform is not installed or not in PATH")
            print("Download from: https://www.terraform.io/downloads.html")
            input("\nPress Enter to continue...")
            return

        print("✓ Terraform is installed")

        # Create Terraform configuration files
        tf_dir = Path("infrastructure")
        tf_dir.mkdir(exist_ok=True)

        # Create main.tf
        main_tf_content = '''# Terraform configuration for your project
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

# Security Group for Web Servers
resource "aws_security_group" "web" {
  name_prefix = "${var.project_name}-web-"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-web-sg"
  }
}

# Output the VPC ID
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public.id
}
'''

        with open(tf_dir / "main.tf", "w") as f:
            f.write(main_tf_content)

        # Create variables.tf
        vars_tf_content = '''# Variables for Terraform configuration

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "magic-cli-project"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}
'''

        with open(tf_dir / "variables.tf", "w") as f:
            f.write(vars_tf_content)

        # Create terraform.tfvars as an example
        tfvars_content = '''# Terraform variables file
project_name = "magic-cli-project"
aws_region   = "us-east-1"
environment  = "dev"
'''

        with open(tf_dir / "terraform.tfvars", "w") as f:
            f.write(tfvars_content)

        print(f"\n✓ Terraform configuration created in '{tf_dir}' directory")
        print("Files created:")
        print(f"  - {tf_dir}/main.tf: Main Terraform configuration")
        print(f"  - {tf_dir}/variables.tf: Input variables")
        print(f"  - {tf_dir}/terraform.tfvars: Variable values")
        print("\nTo use Terraform:")
        print(f"  cd {tf_dir}")
        print("  terraform init")
        print("  terraform plan")
        print("  terraform apply")

        input("\nPress Enter to continue...")

    def setup_docker_registry(self) -> None:
        """Help set up Docker registry integration"""
        print("\n" + "="*70)
        print("DOCKER REGISTRY INTEGRATION")
        print("="*70)

        print("\nThis tool helps integrate with Docker registries.")

        # Check if Docker is installed
        result = subprocess.run(['docker', '--version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ Docker is not installed or not in PATH")
            print("Please install Docker Desktop or Docker Engine")
            input("\nPress Enter to continue...")
            return

        print("✓ Docker is installed")

        print("\nCommon Docker registry options:")
        print("  1. Docker Hub")
        print("  2. Amazon ECR (Elastic Container Registry)")
        print("  3. Google Container Registry")
        print("  4. Azure Container Registry")
        print("  5. Self-hosted registry")

        try:
            choice = input("\nEnter choice (1-5) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_docker_hub()
            elif choice == "2":
                self._setup_aws_ecr()
            elif choice == "3":
                self._setup_gcr()
            elif choice == "4":
                self._setup_acr()
            elif choice == "5":
                self._setup_self_hosted_registry()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_docker_hub(self) -> None:
        """Setup Docker Hub integration"""
        print("\nSetting up Docker Hub integration...")

        username = input("Enter Docker Hub username: ").strip()
        if not username:
            print("Username is required!")
            return

        print(f"\nExample Docker image build and push commands:")
        print(f"  docker build -t {username}/your-app:latest .")
        print(f"  docker push {username}/your-app:latest")

        # Create example build script
        script_content = f'''#!/bin/bash
# Example build and push script for Docker Hub

IMAGE_NAME={username}/magic-cli-app
VERSION=$(git describe --tags --always)

echo "Building $IMAGE_NAME:$VERSION..."
docker build -t $IMAGE_NAME:$VERSION .
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

echo "Pushing to Docker Hub..."
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:latest

echo "Done!"
'''

        with open("build_and_push_docker.sh", "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        try:
            os.chmod("build_and_push_docker.sh", 0o755)
        except:
            pass  # Skip on Windows

        print("✓ Build script created: build_and_push_docker.sh")

    def _setup_aws_ecr(self) -> None:
        """Setup AWS ECR integration"""
        print("\nSetting up AWS ECR integration...")

        print("\nAWS ECR requires AWS CLI to be configured.")
        print("Ensure you have AWS credentials configured using 'aws configure'.")

        # Check if AWS CLI is installed
        result = subprocess.run(['aws', 'configure', 'list'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ AWS CLI is not installed or not configured")
            print("Install and configure AWS CLI to use ECR")
            return

        account_id = input("Enter AWS Account ID: ").strip()
        region = input("Enter AWS Region (e.g., us-east-1): ").strip() or "us-east-1"

        if not account_id:
            print("Account ID is required!")
            return

        print(f"\nExample ECR commands:")
        print(f"  aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com")
        print(f"  docker build -t my-app .")
        print(f"  docker tag my-app:latest {account_id}.dkr.ecr.{region}.amazonaws.com/my-app:latest")
        print(f"  docker push {account_id}.dkr.ecr.{region}.amazonaws.com/my-app:latest")

        # Create example script
        script_content = f'''#!/bin/bash
# Example build and push script for AWS ECR

AWS_ACCOUNT_ID={account_id}
AWS_REGION={region}
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
IMAGE_NAME=magic-cli-app
VERSION=$(git describe --tags --always | head -c 7)

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build the image
docker build -t $IMAGE_NAME .

# Tag the image
docker tag $IMAGE_NAME:latest $ECR_REGISTRY/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME:latest $ECR_REGISTRY/$IMAGE_NAME:latest

# Push the image
docker push $ECR_REGISTRY/$IMAGE_NAME:$VERSION
docker push $ECR_REGISTRY/$IMAGE_NAME:latest

echo "Image pushed to $ECR_REGISTRY/$IMAGE_NAME"
'''

        with open("build_and_push_ecr.sh", "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        try:
            os.chmod("build_and_push_ecr.sh", 0o755)
        except:
            pass  # Skip on Windows

        print("✓ Build script created: build_and_push_ecr.sh")

    def _setup_gcr(self) -> None:
        """Setup Google Container Registry"""
        print("\nSetting up Google Container Registry...")

        print("\nGCR requires gcloud CLI to be installed and authenticated.")
        print("Ensure you're logged in with 'gcloud auth login'.")

        project_id = input("Enter Google Cloud Project ID: ").strip()

        if not project_id:
            print("Project ID is required!")
            return

        print(f"\nExample GCR commands:")
        print(f"  gcloud auth configure-docker")
        print(f"  docker build -t gcr.io/{project_id}/my-app .")
        print(f"  docker push gcr.io/{project_id}/my-app")

        # Create example script
        script_content = f'''#!/bin/bash
# Example build and push script for Google Container Registry

PROJECT_ID={project_id}
IMAGE_NAME=magic-cli-app
VERSION=$(git describe --tags --always | head -c 7)

# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Build the image
docker build -t $IMAGE_NAME .

# Tag the image
docker tag $IMAGE_NAME gcr.io/$PROJECT_ID/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

# Push the image
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:$VERSION
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

echo "Image pushed to gcr.io/$PROJECT_ID/$IMAGE_NAME"
'''

        with open("build_and_push_gcr.sh", "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        try:
            os.chmod("build_and_push_gcr.sh", 0o755)
        except:
            pass  # Skip on Windows

        print("✓ Build script created: build_and_push_gcr.sh")

    def _setup_acr(self) -> None:
        """Setup Azure Container Registry"""
        print("\nSetting up Azure Container Registry...")

        print("\nACR requires Azure CLI to be installed and authenticated.")
        print("Ensure you're logged in with 'az login'.")

        registry_name = input("Enter Azure Container Registry name: ").strip()
        resource_group = input("Enter Azure Resource Group name: ").strip()

        if not registry_name or not resource_group:
            print("Registry name and resource group are required!")
            return

        print(f"\nExample ACR commands:")
        print(f"  az acr login --name {registry_name}")
        print(f"  docker build -t {registry_name}.azurecr.io/my-app .")
        print(f"  docker push {registry_name}.azurecr.io/my-app")

        # Create example script
        script_content = f'''#!/bin/bash
# Example build and push script for Azure Container Registry

ACR_NAME={registry_name}
RESOURCE_GROUP={resource_group}
IMAGE_NAME=magic-cli-app
VERSION=$(git describe --tags --always | head -c 7)

# Login to ACR
az acr login --name $ACR_NAME

# Build the image
docker build -t $IMAGE_NAME .

# Tag the image
docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:latest

# Push the image
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:$VERSION
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:latest

echo "Image pushed to $ACR_NAME.azurecr.io/$IMAGE_NAME"
'''

        with open("build_and_push_acr.sh", "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        try:
            os.chmod("build_and_push_acr.sh", 0o755)
        except:
            pass  # Skip on Windows

        print("✓ Build script created: build_and_push_acr.sh")

    def _setup_self_hosted_registry(self) -> None:
        """Setup self-hosted Docker registry"""
        print("\nSetting up self-hosted Docker registry...")

        registry_url = input("Enter registry URL (e.g., myregistrydomain.com:5000): ").strip()

        if not registry_url:
            print("Registry URL is required!")
            return

        print(f"\nExample commands for self-hosted registry:")
        print(f"  docker build -t {registry_url}/my-app .")
        print(f"  docker push {registry_url}/my-app")

        # Create example script
        script_content = f'''#!/bin/bash
# Example build and push script for self-hosted Docker registry

REGISTRY_URL={registry_url}
IMAGE_NAME=magic-cli-app
VERSION=$(git describe --tags --always | head -c 7)

# Build the image
docker build -t $IMAGE_NAME .

# Tag the image
docker tag $IMAGE_NAME $REGISTRY_URL/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME $REGISTRY_URL/$IMAGE_NAME:latest

# Push the image
docker push $REGISTRY_URL/$IMAGE_NAME:$VERSION
docker push $REGISTRY_URL/$IMAGE_NAME:latest

echo "Image pushed to $REGISTRY_URL/$IMAGE_NAME"
'''

        with open("build_and_push_self_hosted.sh", "w") as f:
            f.write(script_content)

        # Make executable on Unix systems
        try:
            os.chmod("build_and_push_self_hosted.sh", 0o755)
        except:
            pass  # Skip on Windows

        print("✓ Build script created: build_and_push_self_hosted.sh")

    def deploy_to_cloud(self) -> None:
        """Help with deployment to cloud platforms"""
        print("\n" + "="*70)
        print("CLOUD DEPLOYMENT TOOLS")
        print("="*70)

        print("\nDeployment options:")
        print("  1. AWS Elastic Beanstalk")
        print("  2. Google Cloud Run")
        print("  3. Azure App Service")
        print("  4. Heroku")
        print("  5. Digital Ocean App Platform")

        try:
            choice = input("\nEnter choice (1-5) or press Enter to cancel: ").strip()

            if choice == "1":
                self._deploy_to_aws_eb()
            elif choice == "2":
                self._deploy_to_gcp_cloud_run()
            elif choice == "3":
                self._deploy_to_azure_app_service()
            elif choice == "4":
                self._deploy_to_heroku()
            elif choice == "5":
                self._deploy_to_do_app_platform()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _deploy_to_aws_eb(self) -> None:
        """Deploy to AWS Elastic Beanstalk"""
        print("\nDeploying to AWS Elastic Beanstalk...")

        print("\nThis requires the EB CLI (Elastic Beanstalk Command Line Interface).")
        print("Install with: pip install awsebcli")

        # Check if EB CLI is installed
        result = subprocess.run(['eb', '--version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ EB CLI is not installed")
            install = input("Install EB CLI? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "awsebcli"], check=True)
                    print("✓ EB CLI installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install EB CLI")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without EB CLI.")
                input("\nPress Enter to continue...")
                return

        print("\nDeployment steps:")
        print("  1. Navigate to your project directory")
        print("  2. Run: eb init")
        print("  3. Configure your application")
        print("  4. Run: eb create my-environment")
        print("  5. Deploy: eb deploy")

        # Create example requirements file specific for EB
        requirements_content = '''# Requirements for Elastic Beanstalk deployment
# This might differ from your development requirements

fastapi==0.100.0
uvicorn==0.22.0
gunicorn==21.2.0
python-dotenv==1.0.0
'''

        with open("requirements.txt.eb", "w") as f:
            f.write(requirements_content)

        print("✓ Created requirements.txt.eb with common EB requirements")

        print("\nFor WSGI apps, create a .ebextensions/01_settings.config file:")
        eb_config_content = '''option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: src.main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
'''

        eb_ext_dir = Path(".ebextensions")
        eb_ext_dir.mkdir(exist_ok=True)
        with open(eb_ext_dir / "01_settings.config", "w") as f:
            f.write(eb_config_content)

        print("✓ Created .ebextensions/01_settings.config for Python app")

    def _deploy_to_gcp_cloud_run(self) -> None:
        """Deploy to Google Cloud Run"""
        print("\nDeploying to Google Cloud Run...")

        print("\nThis requires gcloud CLI to be installed and authenticated.")
        print("Ensure you're logged in with 'gcloud auth login'.")

        # Check if gcloud is available
        result = subprocess.run(['gcloud', 'version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ gcloud CLI is not installed")
            print("Download from: https://cloud.google.com/sdk/docs/install")
            input("\nPress Enter to continue...")
            return

        service_name = input("Enter service name: ").strip()
        project_id = input("Enter Google Cloud Project ID: ").strip()

        if not service_name or not project_id:
            print("Service name and project ID are required!")
            input("\nPress Enter to continue...")
            return

        print(f"\nDeployment command:")
        print(f"  gcloud run deploy {service_name} --image gcr.io/{project_id}/my-app --platform managed --region us-central1 --project {project_id}")

        print(f"\nFor building and deploying in one command:")
        print(f"  gcloud run deploy {service_name} --source . --platform managed --region us-central1 --project {project_id}")

        # Create example cloudbuild.yaml
        cloudbuild_content = f'''steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/{project_id}/{service_name}', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/{project_id}/{service_name}']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - '{service_name}'
  - '--image'
  - 'gcr.io/{project_id}/{service_name}'
  - '--platform'
  - 'managed'
  - '--region'
  - 'us-central1'
  - '--project'
  - '{project_id}'
  - '--allow-unauthenticated'
'''

        with open("cloudbuild.yaml", "w") as f:
            f.write(cloudbuild_content)

        print("✓ Created cloudbuild.yaml for automated builds")

    def _deploy_to_azure_app_service(self) -> None:
        """Deploy to Azure App Service"""
        print("\nDeploying to Azure App Service...")

        print("\nThis requires Azure CLI and the webapp extension.")
        print("Install with: az extension add --name webapp")

        # Check if az is available
        result = subprocess.run(['az', '--version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ Azure CLI is not installed")
            print("Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            input("\nPress Enter to continue...")
            return

        app_name = input("Enter app name: ").strip()
        resource_group = input("Enter resource group name: ").strip()

        if not app_name or not resource_group:
            print("App name and resource group are required!")
            input("\nPress Enter to continue...")
            return

        print(f"\nDeployment commands:")
        print(f"  az webapp create --resource-group {resource_group} --name {app_name} --runtime 'PYTHON:3.11' --deployment-local-git")

        print("\nFor deployment, you can use:")
        print(f"  git push azure main")
        print("  or")
        print(f"  az webapp deployment source config-zip --resource-group {resource_group} --name {app_name} --src app.zip")

    def _deploy_to_heroku(self) -> None:
        """Deploy to Heroku"""
        print("\nDeploying to Heroku...")

        print("\nThis requires the Heroku CLI.")
        print("Install from: https://devcenter.heroku.com/articles/heroku-cli")

        # Check if heroku is available
        result = subprocess.run(['heroku', '--version'],
                              capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ Heroku CLI is not installed")
            print("Install from: https://devcenter.heroku.com/articles/heroku-cli")
            input("\nPress Enter to continue...")
            return

        app_name = input("Enter app name (or leave empty to generate): ").strip()

        print(f"\nDeployment steps:")
        if app_name:
            print(f"  1. heroku create {app_name}")
        else:
            print(f"  1. heroku create  # This will generate a name")

        print(f"  2. git add .")
        print(f"  3. git commit -m 'Deploy to Heroku'")
        print(f"  4. git push heroku main")

        # Create example Procfile for Heroku
        procfile_content = '''# Procfile for Heroku deployment
web: gunicorn src.main:app --bind 0.0.0.0:$PORT
'''

        with open("Procfile", "w") as f:
            f.write(procfile_content)

        print("✓ Created Procfile for Heroku deployment")

        # Create requirements.txt if it doesn't exist
        if not Path("requirements.txt").exists():
            with open("requirements.txt", "w") as f:
                f.write("fastapi==0.100.0\nuvicorn==0.22.0\ngunicorn==21.2.0\n")

    def _deploy_to_do_app_platform(self) -> None:
        """Deploy to Digital Ocean App Platform"""
        print("\nDeploying to Digital Ocean App Platform...")

        print("\nDigital Ocean App Platform deployments are typically done through:")
        print("  1. The Digital Ocean Control Panel")
        print("  2. Using their API")
        print("  3. Linking to a GitHub/GitLab repository")

        print(f"\nRequired files for Python app:")

        # Create example app spec
        app_spec_content = '''name: my-app
services:
- name: web
  github:
    repo: your-username/your-repo
    branch: main
  run_command: gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
  environment_slug: python
  build_command: pip install -r requirements.txt
  run_command: gunicorn src.main:app -w 4 -b 0.0.0.0:$PORT
  http_port: 8080
'''

        with open("app.yaml", "w") as f:
            f.write(app_spec_content)

        print("✓ Created app.yaml specification file")

        print("\nFor Git-based deployment:")
        print("  1. Create a Dockerfile (if needed)")
        print("  2. Create this app.yaml specification")
        print("  3. Push to GitHub/GitLab")
        print("  4. Link repository in Digital Ocean App Platform")

    def manage_environments(self) -> None:
        """Manage different deployment environments"""
        print("\n" + "="*70)
        print("ENVIRONMENT MANAGEMENT")
        print("="*70)

        print("\nEnvironment management involves:")
        print("  - Configuration files for different environments")
        print("  - Environment-specific variables")
        print("  - Deployment scripts for each environment")

        print("\nCommon environments:")
        print("  - Development (dev)")
        print("  - Staging/Testing (stg/test)")
        print("  - Production (prod)")

        print("\nCreating environment-specific configuration files...")

        # Create environment-specific configs
        env_configs = {
            'development': {
                'DEBUG': 'True',
                'DATABASE_URL': 'sqlite:///./dev.db',
                'LOG_LEVEL': 'DEBUG'
            },
            'staging': {
                'DEBUG': 'False',
                'DATABASE_URL': 'postgresql://user:pwd@staging-db:5432/app',
                'LOG_LEVEL': 'INFO'
            },
            'production': {
                'DEBUG': 'False',
                'DATABASE_URL': 'postgresql://user:pwd@prod-db:5432/app',
                'LOG_LEVEL': 'WARNING'
            }
        }

        for env_name, config_vars in env_configs.items():
            config_content = f"# {env_name.title()} environment configuration\n"
            for key, value in config_vars.items():
                config_content += f"{key}={value}\n"

            with open(f".env.{env_name}", "w") as f:
                f.write(config_content)

            print(f"  - Created .env.{env_name}")

        print("\nEnvironment-specific Docker Compose files...")

        # Create environment-specific docker-compose files
        dev_compose_content = '''version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - ENV=development
    volumes:
      - .:/app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
    ports:
      - "5432:5432"
    volumes:
      - dev_postgres_data:/var/lib/postgresql/data/

volumes:
  dev_postgres_data:
'''

        with open("docker-compose.dev.yml", "w") as f:
            f.write(dev_compose_content)

        prod_compose_content = '''version: '3.8'

services:
  web:
    image: your-registry/your-app:latest
    ports:
      - "80:8000"
    environment:
      - DEBUG=0
      - ENV=production
      - DATABASE_URL=postgresql://prod-user:pwd@prod-db:5432/proddb
    restart: unless-stopped
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: proddb
      POSTGRES_USER: produser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - prod_postgres_data:/var/lib/postgresql/data/
    restart: unless-stopped

volumes:
  prod_postgres_data:
'''

        with open("docker-compose.prod.yml", "w") as f:
            f.write(prod_compose_content)

        print("  - Created docker-compose.dev.yml")
        print("  - Created docker-compose.prod.yml")

        print(f"\nTo use environment configs:")
        print(f"  - For development: docker-compose -f docker-compose.dev.yml up")
        print(f"  - For production: docker-compose -f docker-compose.prod.yml up")

        input("\nPress Enter to continue...")
class DevOpsMenu(Menu):
    """Menu for DevOps tools"""

    def __init__(self):
        self.devops = DevOpsTools()
        super().__init__("DevOps & Infrastructure Tools")

    def setup_items(self) -> None:
        """Setup menu items for DevOps tools"""
        self.items = [
            MenuItem("Setup Terraform Configuration", self.devops.setup_terraform_config),
            MenuItem("Setup Docker Registry Integration", self.devops.setup_docker_registry),
            MenuItem("Deploy to Cloud Platform", self.devops.deploy_to_cloud),
            MenuItem("Manage Environments", self.devops.manage_environments),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]