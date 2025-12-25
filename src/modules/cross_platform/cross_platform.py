"""
Cross-Platform Development Module
Handles mobile app development (React Native, Flutter), desktop app development (Electron, Tauri),
game development tools, and IoT development workflows
"""
import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator


class CrossPlatformTools:
    """Handles cross-platform development tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def setup_mobile_development(self) -> None:
        """Help set up mobile development environment"""
        print("\n" + "=" * 70)
        print("MOBILE APP DEVELOPMENT SETUP")
        print("=" * 70)

        print("\nMobile development options:")
        print("  1. React Native")
        print("  2. Flutter")
        print("  3. NativeScript")
        print("  4. Ionic")

        try:
            choice = input(
                "\nEnter choice (1-4) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_react_native()
            elif choice == "2":
                self._setup_flutter()
            elif choice == "3":
                self._setup_nativescript()
            elif choice == "4":
                self._setup_ionic()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_react_native(self) -> None:
        """Setup React Native development"""
        print("\nSetting up React Native development...")

        # Check if Node.js and npm are available
        try:
            node_result = subprocess.run(['node', '--version'],
                                         capture_output=True, text=True)
            npm_result = subprocess.run(['npm', '--version'],
                                        capture_output=True, text=True)

            if node_result.returncode != 0 or npm_result.returncode != 0:
                print("⚠ Node.js and/or npm are not installed")
                print("Install Node.js from: https://nodejs.org/")
                return
        except FileNotFoundError:
            print("⚠ Node.js and/or npm are not installed")
            print("Install Node.js from: https://nodejs.org/")
            return

        print("✓ Node.js and npm are installed")

        # Check if React Native CLI is available
        try:
            result = subprocess.run(['npx', 'react-native', '--version'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                install = input(
                    "React Native CLI not found. Install globally? (y/n): ").lower()
                if install == 'y':
                    subprocess.run([sys.executable, "-m", "pip",
                                   "install", "nodejs"], check=True)
                    subprocess.run(
                        ['npm', 'install', '-g', 'react-native-cli'],
                        check=True)
                    print("✓ React Native CLI installed")
        except BaseException:
            print("⚠ Could not install React Native CLI")
            print("Try installing manually: npm install -g react-native-cli")
            return

        print("\nTo create a new React Native project:")
        print("  npx react-native init ProjectName")
        print("\nFor development:")
        print("  cd ProjectName")
        print("  npx react-native run-ios      # For iOS")
        print("  npx react-native run-android  # For Android")

        # Create example project setup script
        setup_script = '''#!/bin/bash
# React Native Setup Script
set -e

echo "Creating new React Native project..."

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

echo "Creating project: $PROJECT_NAME"
npx react-native init "$PROJECT_NAME"

cd "$PROJECT_NAME"

echo "Project created successfully!"
echo "To run on iOS: npx react-native run-ios"
echo "To run on Android: npx react-native run-android"
'''

        with open("create_react_native.sh", "w") as f:
            f.write(setup_script)

        # Make executable on Unix systems
        try:
            os.chmod("create_react_native.sh", 0o755)
        except BaseException:
            pass  # Skip on Windows

        print("✓ Created 'create_react_native.sh' setup script")

    def _setup_flutter(self) -> None:
        """Setup Flutter development"""
        print("\nSetting up Flutter development...")

        # Check if Flutter is available
        result = subprocess.run(['flutter', '--version'],
                                capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ Flutter is not installed")
            print("Install from: https://flutter.dev/docs/get-started/install")
            print("\nAfter installation, run 'flutter doctor' to verify setup")
            return

        print("✓ Flutter is installed")

        # Show Flutter doctor output
        print("\nRunning 'flutter doctor' to check setup:")
        result = subprocess.run(['flutter', 'doctor'],
                                capture_output=True, text=True)
        print(result.stdout)

        print("\nTo create a new Flutter project:")
        print("  flutter create project_name")
        print("\nFor development:")
        print("  cd project_name")
        print("  flutter run")

        # Create example project setup script
        setup_script = '''#!/bin/bash
# Flutter Setup Script
set -e

echo "Creating new Flutter project..."

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

echo "Creating project: $PROJECT_NAME"
flutter create "$PROJECT_NAME"

cd "$PROJECT_NAME"

echo "Project created successfully!"
echo "To run: flutter run"
'''

        with open("create_flutter.sh", "w") as f:
            f.write(setup_script)

        # Make executable on Unix systems
        try:
            os.chmod("create_flutter.sh", 0o755)
        except BaseException:
            pass  # Skip on Windows

        print("✓ Created 'create_flutter.sh' setup script")

    def _setup_nativescript(self) -> None:
        """Setup NativeScript development"""
        print("\nSetting up NativeScript development...")

        # Check if Node.js is available
        try:
            result = subprocess.run(['node', '--version'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Node.js is not installed")
                print("Install Node.js from: https://nodejs.org/")
                return
        except FileNotFoundError:
            print("⚠ Node.js is not installed")
            print("Install Node.js from: https://nodejs.org/")
            return

        print("✓ Node.js is installed")

        # Check if NativeScript CLI is available
        result = subprocess.run(['ns', '--version'],
                                capture_output=True, text=True)

        if result.returncode != 0:
            install = input(
                "NativeScript CLI not found. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run(
                        ['npm', 'install', '-g', 'nativescript'], check=True)
                    print("✓ NativeScript CLI installed")
                except subprocess.CalledProcessError:
                    print("⚠ Could not install NativeScript CLI")
                    return
        else:
            print("✓ NativeScript CLI is installed")

        print("\nTo create a new NativeScript project:")
        print("  ns create project-name --vue  # For Vue.js template")
        print("  ns create project-name --react  # For React template")
        print("\nFor development:")
        print("  cd project-name")
        print("  ns run android")
        print("  ns run ios")

    def _setup_ionic(self) -> None:
        """Setup Ionic development"""
        print("\nSetting up Ionic development...")

        # Check if Node.js and npm are available
        try:
            node_result = subprocess.run(['node', '--version'],
                                         capture_output=True, text=True)
            npm_result = subprocess.run(['npm', '--version'],
                                        capture_output=True, text=True)

            if node_result.returncode != 0 or npm_result.returncode != 0:
                print("⚠ Node.js and/or npm are not installed")
                print("Install Node.js from: https://nodejs.org/")
                return
        except FileNotFoundError:
            print("⚠ Node.js and/or npm are not installed")
            print("Install Node.js from: https://nodejs.org/")
            return

        print("✓ Node.js and npm are installed")

        # Check if Ionic CLI is available
        result = subprocess.run(['ionic', '--version'],
                                capture_output=True, text=True)

        if result.returncode != 0:
            install = input(
                "Ionic CLI not found. Install globally? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run(
                        ['npm', 'install', '-g', '@ionic/cli'], check=True)
                    print("✓ Ionic CLI installed")
                except subprocess.CalledProcessError:
                    print("⚠ Could not install Ionic CLI")
                    return
        else:
            print("✓ Ionic CLI is installed")

        print("\nTo create a new Ionic project:")
        print("  ionic start project-name")
        print("\nFor development:")
        print("  cd project-name")
        print("  ionic serve  # For web")
        print("  ionic capacitor run android  # For Android")
        print("  ionic capacitor run ios  # For iOS")

    def setup_desktop_development(self) -> None:
        """Help set up desktop application development"""
        print("\n" + "=" * 70)
        print("DESKTOP APP DEVELOPMENT SETUP")
        print("=" * 70)

        print("\nDesktop development options:")
        print("  1. Electron (JavaScript/TypeScript)")
        print("  2. Tauri (Rust + Web Tech)")
        print("  3. PyInstaller (Python to Executables)")
        print("  4. Flutter Desktop")

        try:
            choice = input(
                "\nEnter choice (1-4) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_electron()
            elif choice == "2":
                self._setup_tauri()
            elif choice == "3":
                self._setup_pyinstaller()
            elif choice == "4":
                self._setup_flutter_desktop()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_electron(self) -> None:
        """Setup Electron development"""
        print("\nSetting up Electron development...")

        # Check if Node.js and npm are available
        try:
            node_result = subprocess.run(['node', '--version'],
                                         capture_output=True, text=True)
            npm_result = subprocess.run(['npm', '--version'],
                                        capture_output=True, text=True)

            if node_result.returncode != 0 or npm_result.returncode != 0:
                print("⚠ Node.js and/or npm are not installed")
                print("Install Node.js from: https://nodejs.org/")
                return
        except FileNotFoundError:
            print("⚠ Node.js and/or npm are not installed")
            print("Install Node.js from: https://nodejs.org/")
            return

        print("✓ Node.js and npm are installed")

        print("\nTo create a new Electron project:")
        print("  mkdir my-electron-app && cd my-electron-app")
        print("  npm init -y")
        print("  npm install electron --save-dev")

        print("\nFor development:")
        print("  npx electron .")

        print("\nTo package for distribution:")
        print("  npm install electron-builder --save-dev")
        print("  # Add build scripts to package.json")
        print("  npm run dist")

        # Create example package.json
        package_json = '''{
  "name": "my-electron-app",
  "version": "1.0.0",
  "description": "A minimal Electron application",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dist": "electron-builder --dir"
  },
  "devDependencies": {
    "electron": "^latest",
    "electron-builder": "^latest"
  }
}
'''

        with open("electron_package.json", "w") as f:
            f.write(package_json)

        print("✓ Created 'electron_package.json' template")

        # Create example main.js
        main_js = '''const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
'''

        with open("electron_main.js", "w") as f:
            f.write(main_js)

        print("✓ Created 'electron_main.js' example")

    def _setup_tauri(self) -> None:
        """Setup Tauri development"""
        print("\nSetting up Tauri development...")

        # Check if Rust is available
        try:
            result = subprocess.run(['rustc', '--version'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Rust is not installed")
                print("Install from: https://www.rust-lang.org/tools/install")
                return
        except FileNotFoundError:
            print("⚠ Rust is not installed")
            print("Install from: https://www.rust-lang.org/tools/install")
            return

        print("✓ Rust is installed")

        # Check if Node.js is available (for frontend)
        try:
            result = subprocess.run(['node', '--version'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Node.js is not installed (recommended for frontend)")
            else:
                print("✓ Node.js is installed")
        except FileNotFoundError:
            print("⚠ Node.js is not installed (recommended for frontend)")

        print("\nTo install Tauri CLI:")
        print("  cargo install tauri-cli")

        print("\nTo create a new Tauri project:")
        print("  cargo tauri init")

        print("\nFor development:")
        print("  cargo tauri dev")

        print("\nTo build:")
        print("  cargo tauri build")

    def _setup_pyinstaller(self) -> None:
        """Setup PyInstaller for Python executables"""
        print("\nSetting up PyInstaller for Python to executable conversion...")

        # Check if PyInstaller is available
        try:
            import PyInstaller
            print("✓ PyInstaller is already installed")
        except ImportError:
            install = input("PyInstaller not found. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip",
                                   "install", "pyinstaller"], check=True)
                    print("✓ PyInstaller installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install PyInstaller")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without PyInstaller.")
                input("\nPress Enter to continue...")
                return

        print("\nTo create an executable from a Python script:")
        print("  pyinstaller --onefile your_script.py")

        print("\nCommon PyInstaller options:")
        print("  --onefile: Create a single executable file")
        print("  --windowed: Don't open a console window (for GUI apps)")
        print("  --add-data 'src;dest': Add data files to the executable")
        print("  --icon: Specify an icon file")

        # Create example spec file
        spec_content = '''# Sample spec file for PyInstaller
# Generated by Magic CLI

# Use this file to customize your PyInstaller build
# Run with: pyinstaller your_app.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='your_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

        with open("sample_pyinstaller.spec", "w") as f:
            f.write(spec_content)

        print("✓ Created 'sample_pyinstaller.spec' configuration template")

    def _setup_flutter_desktop(self) -> None:
        """Setup Flutter for desktop development"""
        print("\nSetting up Flutter for desktop development...")

        # Check if Flutter is available
        result = subprocess.run(['flutter', '--version'],
                                capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠ Flutter is not installed")
            print("Install from: https://flutter.dev/docs/get-started/install")
            return

        print("✓ Flutter is installed")

        # Enable desktop support
        print("\nEnabling desktop support...")

        platforms = ['windows', 'macos', 'linux']
        for platform in platforms:
            try:
                result = subprocess.run(['flutter',
                                         'config',
                                         f'--enable-{platform}-desktop'],
                                        capture_output=True,
                                        text=True)
                if result.returncode == 0:
                    print(f"✓ Enabled {platform} desktop support")
                else:
                    print(f"⚠ Could not enable {platform} desktop support")
            except BaseException:
                print(f"⚠ Error enabling {platform} desktop support")

        print("\nTo create a new Flutter desktop project:")
        print("  flutter create my_desktop_app")
        print("\nTo run on desktop:")
        print("  cd my_desktop_app")
        print("  flutter run -d windows  # Windows")
        print("  flutter run -d macos    # macOS")
        print("  flutter run -d linux    # Linux")

        print("\nTo build for distribution:")
        print("  flutter build windows  # Windows")
        print("  flutter build macos    # macOS")
        print("  flutter build linux    # Linux")

    def setup_game_development(self) -> None:
        """Help set up game development environment"""
        print("\n" + "=" * 70)
        print("GAME DEVELOPMENT SETUP")
        print("=" * 70)

        print("\nGame development options:")
        print("  1. Unity (C#)")
        print("  2. Godot (GDScript/C#)")
        print("  3. PyGame (Python)")
        print("  4. Three.js (JavaScript/3D)")

        try:
            choice = input(
                "\nEnter choice (1-4) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_unity()
            elif choice == "2":
                self._setup_godot()
            elif choice == "3":
                self._setup_pygame()
            elif choice == "4":
                self._setup_threejs()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_unity(self) -> None:
        """Setup Unity development"""
        print("\nSetting up Unity development...")

        print("Unity Hub: https://unity.com/download")
        print("Unity Editor can be installed via Unity Hub")

        print("\nUnity project structure typically includes:")
        print("  - Assets/: All game assets")
        print("  - ProjectSettings/: Project configuration")
        print("  - Packages/: Package manifests and local packages")

        print("\nTo get started with Unity:")
        print("  1. Download Unity Hub from unity.com/download")
        print("  2. Install Unity Editor through Hub")
        print("  3. Create a new project through Hub")
        print("  4. Import packages via Package Manager")

        print("\nFor version control with Unity:")
        print("  - Use .gitignore template for Unity projects")
        print("  - Consider using Unity Collaborate for team projects")
        print("  - Git LFS for large asset files")

    def _setup_godot(self) -> None:
        """Setup Godot development"""
        print("\nSetting up Godot development...")

        print("Download Godot from: https://godotengine.org/download")

        print("\nGodot project structure typically includes:")
        print("  - project.godot: Project configuration file")
        print("  - res://: Resource path for project files")
        print("  - user://: User data path")

        print("\nTo get started with Godot:")
        print("  1. Download Godot editor from godotengine.org")
        print("  2. Create a new project in the Project Manager")
        print("  3. Use GDScript or C# for scripting")
        print("  4. Export for different platforms via Export menu")

        print("\nFor version control with Godot:")
        print("  - .gitignore should exclude .import/ folder")
        print("  - Consider using Godot's built-in scene system")

    def _setup_pygame(self) -> None:
        """Setup PyGame development"""
        print("\nSetting up PyGame development...")

        # Check if PyGame is available
        try:
            import pygame
            print("✓ PyGame is already installed")
        except ImportError:
            install = input("PyGame not found. Install? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip",
                                   "install", "pygame"], check=True)
                    print("✓ PyGame installed successfully")
                    import pygame
                    print(f"✓ PyGame version: {pygame.version.ver}")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install PyGame")
                    input("\nPress Enter to continue...")
                    return
            else:
                print("Cannot proceed without PyGame.")
                input("\nPress Enter to continue...")
                return

        print("\nExample PyGame project structure:")
        print("  - main.py: Game entry point")
        print("  - game/ or src/: Game logic modules")
        print("  - assets/: Images, sounds, fonts")
        print("  - docs/: Documentation")

        # Create example PyGame code
        pygame_example = '''import pygame
import sys

# Initialize PyGame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([500, 500])

# Run until the user asks to quit
running = True
clock = pygame.time.Clock()

while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw a solid blue circle in the center
    pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

    # Flip the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Done! Time to quit.
pygame.quit()
sys.exit()
'''

        with open("pygame_example.py", "w") as f:
            f.write(pygame_example)

        print("✓ Created 'pygame_example.py' sample game")

        print("\nTo run: python pygame_example.py")

    def _setup_threejs(self) -> None:
        """Setup Three.js development"""
        print("\nSetting up Three.js development...")

        # Check if Node.js is available
        try:
            result = subprocess.run(['node', '--version'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠ Node.js is not installed")
                print("Install from: https://nodejs.org/")
                return
        except FileNotFoundError:
            print("⚠ Node.js is not installed")
            print("Install from: https://nodejs.org/")
            return

        print("✓ Node.js is installed")

        print("\nTo start a Three.js project:")
        print("  mkdir threejs-project && cd threejs-project")
        print("  npm init -y")
        print("  npm install three")

        print("\nFor development with a dev server:")
        print("  npm install -D vite")
        print("  npx vite")

        print("\nExample Three.js HTML setup:")
        html_example = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>My Three.js App</title>
    <style>
        body { margin: 0; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script type="module">
        import * as THREE from 'three';

        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Create a cube
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);

        camera.position.z = 5;

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);

            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;

            renderer.render(scene, camera);
        }

        animate();
    </script>
</body>
</html>
'''

        with open("threejs_example.html", "w") as f:
            f.write(html_example)

        print("✓ Created 'threejs_example.html' sample app")

    def setup_iot_development(self) -> None:
        """Help set up IoT development environment"""
        print("\n" + "=" * 70)
        print("IOT DEVELOPMENT SETUP")
        print("=" * 70)

        print("\nIoT development typically involves:")
        print("  - Microcontroller programming (Arduino, ESP32, etc.)")
        print("  - Communication protocols (WiFi, Bluetooth, MQTT)")
        print("  - Cloud integration (AWS IoT, Azure IoT, Google Cloud IoT)")

        print("\nCommon IoT platforms:")
        print("  1. Arduino IDE")
        print("  2. PlatformIO")
        print("  3. Raspberry Pi with Python")
        print("  4. ESP-IDF (Espressif IoT Development Framework)")

        try:
            choice = input(
                "\nEnter choice (1-4) or press Enter to cancel: ").strip()

            if choice == "1":
                self._setup_arduino()
            elif choice == "2":
                self._setup_platformio()
            elif choice == "3":
                self._setup_raspberry_pi()
            elif choice == "4":
                self._setup_esp_idf()
            elif choice == "":
                print("Operation cancelled.")
            else:
                print("Invalid choice. Operation cancelled.")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        input("\nPress Enter to continue...")

    def _setup_arduino(self) -> None:
        """Setup Arduino development"""
        print("\nSetting up Arduino development...")

        print("Download Arduino IDE from: https://www.arduino.cc/en/software")
        print("\nOr use Arduino CLI for headless development:")
        print("  Download from: https://github.com/arduino/arduino-cli")

        print("\nFor Python integration with Arduino:")
        print("  pip install pyfirmata  # For Firmata protocol")
        print("  pip install serial     # For direct serial communication")

        print("\nCommon Arduino libraries:")
        print("  - WiFiNINA: For WiFi connectivity")
        print("  - WiFi101: For older WiFi boards")
        print("  - Ethernet: For Ethernet connectivity")
        print("  - MQTT: For MQTT messaging")
        print("  - Adafruit: For Adafruit hardware")

    def _setup_platformio(self) -> None:
        """Setup PlatformIO development"""
        print("\nSetting up PlatformIO development...")

        # Check if PlatformIO is available
        try:
            result = subprocess.run(['pio', '--version'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ PlatformIO is installed")
            else:
                print("⚠ PlatformIO is not installed")
        except FileNotFoundError:
            print("⚠ PlatformIO is not installed")

        print("\nTo install PlatformIO:")
        print("  pip install -U platformio")

        print("\nTo create a new PlatformIO project:")
        print("  pio project init --board <board-id>")

        print("\nTo build and upload:")
        print("  pio run          # Build project")
        print("  pio run --target upload  # Build and upload")

        print("\nPlatformIO advantages:")
        print("  - Cross-platform IDE")
        print("  - Built-in library manager")
        print("  - Unified debugging experience")
        print("  - Multiple framework support")

    def _setup_raspberry_pi(self) -> None:
        """Setup Raspberry Pi development"""
        print("\nSetting up Raspberry Pi development...")

        print("\nFor Python development with Raspberry Pi:")
        print("  pip install RPi.GPIO  # Raspberry Pi GPIO library")
        print("  pip install gpiozero  # Higher-level GPIO library")
        print("  pip install picamera  # For camera module")

        print("\nFor remote development:")
        print("  - SSH into your Pi: ssh pi@<pi-ip-address>")
        print("  - Use VS Code with Remote SSH extension")
        print("  - Use Thonny IDE for beginner-friendly Python development")

        print("\nCommon Raspberry Pi projects:")
        print("  - Home automation")
        print("  - Media centers")
        print("  - Weather stations")
        print("  - Security cameras")
        print("  - IoT gateways")

    def _setup_esp_idf(self) -> None:
        """Setup ESP-IDF development"""
        print("\nSetting up ESP-IDF development...")

        print("ESP-IDF (Espressif IoT Development Framework)")
        print("For ESP32 family microcontrollers")

        print("\nTo install ESP-IDF:")
        print("  1. Clone from: https://github.com/espressif/esp-idf")
        print("  2. Run install script: ./install.sh")
        print("  3. Set up environment: source export.sh")

        print("\nTo create a new ESP-IDF project:")
        print("  1. Copy template from esp-idf/examples")
        print("  2. Run 'idf.py set-target esp32' (or esp32s3, etc.)")
        print("  3. Build: idf.py build")
        print("  4. Flash to device: idf.py flash")

        print("\nFor VS Code integration:")
        print("  - Install Espressif IDF extension")
        print("  - Configure IDF path in settings")


class CrossPlatformMenu(Menu):
    """Menu for cross-platform development tools"""

    def __init__(self):
        self.cross_platform = CrossPlatformTools()
        super().__init__("Cross-Platform Development Tools")

    def setup_items(self) -> None:
        """Setup menu items for cross-platform tools"""
        self.items = [
            MenuItem("Mobile App Development Setup", self.cross_platform.setup_mobile_development),
            MenuItem("Desktop App Development Setup", self.cross_platform.setup_desktop_development),
            MenuItem("Game Development Setup", self.cross_platform.setup_game_development),
            MenuItem("IoT Development Setup", self.cross_platform.setup_iot_development),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]
