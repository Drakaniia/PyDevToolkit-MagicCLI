"""
automation/dev_mode/docker_quick.py
Quick Docker commands for development
"""
import subprocess
from pathlib import Path
from typing import Optional
from automation.dev_mode._base import DevModeCommand
from automation.dev_mode.menu_utils import get_choice_with_arrows


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
            "Build Image",
            "Run Container", 
            "Stop Container",
            "List Running Containers",
            "List All Containers",
            "List Images",
            "Prune Unused Resources",
            "Cancel"
        ]
        
        choice = get_choice_with_arrows(docker_options, "Docker Operations")
        
        if choice == 1:
            self._build_image()
        elif choice == 2:
            self._run_container()
        elif choice == 3:
            self._stop_container()
        elif choice == 4:
            self._list_containers(all_containers=False)
        elif choice == 5:
            self._list_containers(all_containers=True)
        elif choice == 6:
            self._list_images()
        elif choice == 7:
            self._prune_resources()
        elif choice == 8:
            print("\n❌ Operation cancelled")
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")
    
    def _noninteractive_docker(self, operation: str, **kwargs):
        """Non-interactive Docker operations"""
        operations = {
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
            dockerfile = input("Dockerfile path (default: ./Dockerfile): ").strip() or 'Dockerfile'
            
            # Get build context
            context = input("Build context (default: .): ").strip() or '.'
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
        
        # Build command
        cmd = ['docker', 'build', '-t', image_name, '-f', dockerfile, context]
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
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


# Export command instance
COMMAND = DockerQuickCommand()  