"""
automation/dev_mode/create_frontend.py
Create new frontend projects (React, Next.js, Vue)
FIXED: Windows compatibility for npx/npm commands
"""
import subprocess
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from ._base import DevModeCommand
from .menu_utils import get_choice_with_arrows
class CreateFrontendCommand(DevModeCommand):
    """Command to create new frontend projects"""

    label = "Create Frontend Project (Web & Mobile)"
    description = "Scaffold a new frontend project using modern frameworks for web and mobile"

    FRAMEWORKS = {
        # Web Frameworks
        '1': {'name': 'React', 'command': 'create-react-app', 'type': 'web'},
        '2': {'name': 'Next.js', 'command': 'create-next-app', 'type': 'web'},
        '3': {'name': 'Vue.js', 'command': 'create-vue', 'type': 'web'},
        '4': {'name': 'Angular', 'command': '@angular/cli', 'type': 'web'},
        '5': {'name': 'Svelte', 'command': 'create-svelte', 'type': 'web'},
        '6': {'name': 'SvelteKit', 'command': 'create-svelte', 'type': 'web'},
        '7': {'name': 'Nuxt.js (Vue)', 'command': 'create-nuxt-app', 'type': 'web'},
        '8': {'name': 'Vite (Vanilla)', 'command': 'create-vite', 'type': 'web'},
        '9': {'name': 'Astro', 'command': 'create-astro', 'type': 'web'},
        '10': {'name': 'Remix', 'command': 'create-remix', 'type': 'web'},
        '11': {'name': 'Gatsby', 'command': 'create-gatsby', 'type': 'web'},
        '12': {'name': 'Solid.js', 'command': 'create-solid', 'type': 'web'},
        '13': {'name': 'Qwik', 'command': 'create-qwik', 'type': 'web'},

        # Mobile Frameworks
        '14': {'name': 'React Native', 'command': 'react-native', 'type': 'mobile'},
        '15': {'name': 'Expo (React Native)', 'command': 'create-expo-app', 'type': 'mobile'},
        '16': {'name': 'Ionic React', 'command': 'ionic', 'type': 'mobile'},
        '17': {'name': 'Ionic Angular', 'command': 'ionic', 'type': 'mobile'},
        '18': {'name': 'Ionic Vue', 'command': 'ionic', 'type': 'mobile'},
        '19': {'name': 'Flutter (Web)', 'command': 'flutter', 'type': 'mobile'},
        '20': {'name': 'Capacitor + React', 'command': 'capacitor', 'type': 'mobile'},
        '21': {'name': 'Capacitor + Vue', 'command': 'capacitor', 'type': 'mobile'},
        '22': {'name': 'NativeScript', 'command': 'nativescript', 'type': 'mobile'},

        # Full-Stack/Meta Frameworks
        '23': {'name': 'T3 Stack (Next.js + tRPC)', 'command': 'create-t3-app', 'type': 'fullstack'},
        '24': {'name': 'Blitz.js', 'command': 'create-blitz-app', 'type': 'fullstack'},
        '25': {'name': 'RedwoodJS', 'command': 'create-redwood-app', 'type': 'fullstack'}
    }

    PACKAGE_MANAGERS = {
        '1': 'npm',
        '2': 'pnpm',
        '3': 'yarn'
    }

    CSS_FRAMEWORKS = {
        '1': {'name': 'None', 'flag': None},
        '2': {'name': 'Tailwind CSS', 'flag': '--tailwind'},
        '3': {'name': 'Bootstrap', 'flag': None},
        '4': {'name': 'Material-UI / MUI', 'flag': None},
        '5': {'name': 'Chakra UI', 'flag': None},
        '6': {'name': 'Ant Design', 'flag': None},
        '7': {'name': 'Styled Components', 'flag': None},
        '8': {'name': 'Emotion', 'flag': None}
    }

    def run(self, interactive: bool = True, **kwargs) -> Any:
        """Execute frontend project creation"""
        if interactive:
            return self._interactive_create()
        else:
            return self._noninteractive_create(**kwargs)

    def _interactive_create(self):
        """Interactive project creation flow"""
        print("\n" + "="*70)
        print("CREATE FRONTEND PROJECT")
        print("="*70 + "\n")

        # Check if Node.js/npm is installed
        if not self.validate_binary('node'):
            self.show_missing_binary_error(
                'node',
                'https://nodejs.org/'
            )
            input("\nPress Enter to continue...")
            return

        # 1. Select framework
        framework_choice = self._prompt_framework()
        if not framework_choice:
            return

        framework_info = self.FRAMEWORKS[framework_choice]

        # 2. Get project name
        project_name = self._prompt_project_name()
        if not project_name:
            return

        # 3. Select package manager
        pkg_manager = self._prompt_package_manager()
        if not pkg_manager:
            return

        # 4. TypeScript?
        use_typescript = self._prompt_yes_no("Use TypeScript?", default='y')
        if use_typescript is None:
            return

        # 5. CSS Framework
        css_choice = self._prompt_css_framework()
        if not css_choice:
            return
        css_info = self.CSS_FRAMEWORKS[css_choice]

        # 6. Target directory
        target_dir = self._prompt_directory()
        if not target_dir:
            return

        # 7. Initialize Git?
        init_git = self._prompt_yes_no("Initialize Git repository?", default='y')
        if init_git is None:
            return

        # Show summary
        print("\n" + "="*70)
        print("PROJECT SUMMARY")
        print("="*70)
        print(f"Framework:        {framework_info['name']}")
        print(f"Project Name:     {project_name}")
        print(f"Package Manager:  {pkg_manager}")
        print(f"TypeScript:       {'Yes' if use_typescript else 'No'}")
        print(f"CSS Framework:    {css_info['name']}")
        print(f"Target Directory: {target_dir}")
        print(f"Initialize Git:   {'Yes' if init_git else 'No'}")
        print("="*70 + "\n")

        confirm = self._prompt_yes_no("Proceed with creation?", default='y')
        if confirm is None or not confirm:
            print("\nProject creation cancelled")
            input("\nPress Enter to continue...")
            return

        # Create project
        self._create_project(
            framework=framework_info,
            project_name=project_name,
            pkg_manager=pkg_manager,
            use_typescript=use_typescript,
            css_framework=css_info,
            target_dir=target_dir,
            init_git=init_git
        )

        input("\nPress Enter to continue...")

    def _noninteractive_create(
        self,
        framework: str,
        name: str,
        package_manager: str = 'npm',
        typescript: bool = False,
        css: str = 'none',
        directory: str = '.',
        init_git: bool = False
    ):
        """Non-interactive project creation"""
        # Validate inputs
        if not name or not self._is_valid_project_name(name):
            raise ValueError(f"Invalid project name: {name}")

        framework_map = {
            # Web frameworks
            'react': self.FRAMEWORKS['1'],
            'next': self.FRAMEWORKS['2'],
            'nextjs': self.FRAMEWORKS['2'],
            'vue': self.FRAMEWORKS['3'],
            'vuejs': self.FRAMEWORKS['3'],
            'angular': self.FRAMEWORKS['4'],
            'svelte': self.FRAMEWORKS['5'],
            'sveltekit': self.FRAMEWORKS['6'],
            'nuxt': self.FRAMEWORKS['7'],
            'nuxtjs': self.FRAMEWORKS['7'],
            'vite': self.FRAMEWORKS['8'],
            'astro': self.FRAMEWORKS['9'],
            'remix': self.FRAMEWORKS['10'],
            'gatsby': self.FRAMEWORKS['11'],
            'solid': self.FRAMEWORKS['12'],
            'solidjs': self.FRAMEWORKS['12'],
            'qwik': self.FRAMEWORKS['13'],

            # Mobile frameworks
            'react-native': self.FRAMEWORKS['14'],
            'rn': self.FRAMEWORKS['14'],
            'expo': self.FRAMEWORKS['15'],
            'ionic-react': self.FRAMEWORKS['16'],
            'ionic-angular': self.FRAMEWORKS['17'],
            'ionic-vue': self.FRAMEWORKS['18'],
            'flutter': self.FRAMEWORKS['19'],
            'capacitor-react': self.FRAMEWORKS['20'],
            'capacitor-vue': self.FRAMEWORKS['21'],
            'nativescript': self.FRAMEWORKS['22'],

            # Full-stack frameworks
            't3': self.FRAMEWORKS['23'],
            't3-stack': self.FRAMEWORKS['23'],
            'blitz': self.FRAMEWORKS['24'],
            'blitzjs': self.FRAMEWORKS['24'],
            'redwood': self.FRAMEWORKS['25'],
            'redwoodjs': self.FRAMEWORKS['25']
        }

        framework_info = framework_map.get(framework.lower())
        if not framework_info:
            raise ValueError(f"Unknown framework: {framework}")

        css_info = self.CSS_FRAMEWORKS['1']  # Default to none

        self._create_project(
            framework=framework_info,
            project_name=name,
            pkg_manager=package_manager,
            use_typescript=typescript,
            css_framework=css_info,
            target_dir=directory,
            init_git=init_git
        )

    def _create_project(
        self,
        framework: Dict,
        project_name: str,
        pkg_manager: str,
        use_typescript: bool,
        css_framework: Dict,
        target_dir: str,
        init_git: bool
    ):
        """Execute project creation"""
        print("\nCreating project...\n")

        target_path = Path(target_dir).resolve()
        project_path = target_path / project_name

        # Check if directory already exists
        if project_path.exists():
            print(f"ERROR: Directory '{project_name}' already exists")
            return

        try:
            # Build command based on framework
            framework_name = framework['name']

            if framework_name == 'React':
                cmd = self._build_react_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Next.js':
                cmd = self._build_nextjs_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Vue.js':
                cmd = self._build_vue_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Angular':
                cmd = self._build_angular_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Svelte':
                cmd = self._build_svelte_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'SvelteKit':
                cmd = self._build_sveltekit_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Nuxt.js (Vue)':
                cmd = self._build_nuxt_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Vite (Vanilla)':
                cmd = self._build_vite_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Astro':
                cmd = self._build_astro_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Remix':
                cmd = self._build_remix_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Gatsby':
                cmd = self._build_gatsby_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Solid.js':
                cmd = self._build_solid_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Qwik':
                cmd = self._build_qwik_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'React Native':
                cmd = self._build_react_native_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Expo (React Native)':
                cmd = self._build_expo_command(project_name, use_typescript, pkg_manager)
            elif 'Ionic' in framework_name:
                cmd = self._build_ionic_command(project_name, framework_name, use_typescript, pkg_manager)
            elif framework_name == 'Flutter (Web)':
                cmd = self._build_flutter_command(project_name, use_typescript, pkg_manager)
            elif 'Capacitor' in framework_name:
                cmd = self._build_capacitor_command(project_name, framework_name, use_typescript, pkg_manager)
            elif framework_name == 'NativeScript':
                cmd = self._build_nativescript_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'T3 Stack (Next.js + tRPC)':
                cmd = self._build_t3_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'Blitz.js':
                cmd = self._build_blitz_command(project_name, use_typescript, pkg_manager)
            elif framework_name == 'RedwoodJS':
                cmd = self._build_redwood_command(project_name, use_typescript, pkg_manager)
            else:
                raise ValueError(f"Unsupported framework: {framework_name}")

            # Execute creation command
            print(f"$ {' '.join(cmd)}\n")

            # Use shell=True on Windows for npx/npm commands
            use_shell = sys.platform == 'win32'

            result = subprocess.run(
                cmd if not use_shell else ' '.join(cmd),
                cwd=target_path,
                check=True,
                capture_output=False,
                shell=use_shell
            )

            print(f"\nProject '{project_name}' created successfully!")

            # Initialize Git if requested
            if init_git:
                self._initialize_git(project_path)

            # Show next steps
            self._show_next_steps(project_name, pkg_manager, framework_name)

        except subprocess.CalledProcessError as e:
            print(f"\nFailed to create project: {e}")
        except Exception as e:
            print(f"\nError: {e}")

    def _build_react_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-react-app command"""
        cmd = ['npx', 'create-react-app', name]
        if typescript:
            cmd.append('--template')
            cmd.append('typescript')
        if pkg_manager != 'npm':
            cmd.extend(['--use-' + pkg_manager])
        return cmd

    def _build_nextjs_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-next-app command"""
        cmd = ['npx', 'create-next-app@latest', name]
        if typescript:
            cmd.append('--typescript')
        else:
            cmd.append('--js')
        cmd.append('--no-git')  # We'll handle git separately
        if pkg_manager != 'npm':
            cmd.extend(['--use-' + pkg_manager])
        return cmd

    def _build_vue_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-vue command"""
        cmd = ['npm', 'init', 'vue@latest', name, '--', '--default']
        if typescript:
            cmd.append('--typescript')
        return cmd

    def _build_angular_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Angular CLI command"""
        cmd = ['npx', '@angular/cli@latest', 'new', name, '--routing=true', '--style=scss']
        if pkg_manager != 'npm':
            cmd.extend(['--package-manager', pkg_manager])
        return cmd

    def _build_svelte_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build create-svelte command"""
        cmd = ['npm', 'create', 'svelte@latest', name]
        return cmd

    def _build_sveltekit_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build SvelteKit command"""
        cmd = ['npm', 'create', 'svelte@latest', name]
        return cmd

    def _build_nuxt_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Nuxt.js command"""
        cmd = ['npx', 'nuxi@latest', 'init', name]
        return cmd

    def _build_vite_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Vite command"""
        template = 'vanilla-ts' if typescript else 'vanilla'
        cmd = ['npm', 'create', 'vite@latest', name, '--', '--template', template]
        return cmd

    def _build_astro_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Astro command"""
        cmd = ['npm', 'create', 'astro@latest', name, '--', '--template', 'minimal']
        if typescript:
            cmd.extend(['--typescript', 'strict'])
        return cmd

    def _build_remix_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Remix command"""
        cmd = ['npx', 'create-remix@latest', name]
        if typescript:
            cmd.extend(['--template', 'typescript'])
        return cmd

    def _build_gatsby_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Gatsby command"""
        cmd = ['npx', 'create-gatsby', name]
        if typescript:
            cmd.extend(['-ts'])
        return cmd

    def _build_solid_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Solid.js command"""
        template = 'ts' if typescript else 'js'
        cmd = ['npx', 'degit', f'solidjs/templates/{template}', name]
        return cmd

    def _build_qwik_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Qwik command"""
        cmd = ['npm', 'create', 'qwik@latest', name]
        return cmd

    def _build_react_native_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build React Native command"""
        cmd = ['npx', 'react-native@latest', 'init', name]
        if typescript:
            cmd.extend(['--template', 'react-native-template-typescript'])
        return cmd

    def _build_expo_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Expo command"""
        template = 'typescript' if typescript else 'blank'
        cmd = ['npx', 'create-expo-app@latest', name, '--template', template]
        return cmd

    def _build_ionic_command(self, name: str, framework_name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Ionic command"""
        if 'React' in framework_name:
            framework_type = 'react'
        elif 'Angular' in framework_name:
            framework_type = 'angular'
        elif 'Vue' in framework_name:
            framework_type = 'vue'
        else:
            framework_type = 'react'  # Default

        cmd = ['npx', '@ionic/cli', 'start', name, 'tabs', '--type', framework_type]
        if pkg_manager != 'npm':
            cmd.extend(['--package-manager', pkg_manager])
        return cmd

    def _build_flutter_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Flutter command"""
        cmd = ['flutter', 'create', name, '--platforms', 'web']
        return cmd

    def _build_capacitor_command(self, name: str, framework_name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Capacitor command"""
        if 'React' in framework_name:
            # First create React app, then add Capacitor
            cmd = ['npx', 'create-react-app', name]
            if typescript:
                cmd.extend(['--template', 'typescript'])
        elif 'Vue' in framework_name:
            # First create Vue app, then add Capacitor
            cmd = ['npm', 'init', 'vue@latest', name, '--', '--default']
            if typescript:
                cmd.append('--typescript')
        else:
            cmd = ['npx', 'create-react-app', name]  # Default to React

        return cmd

    def _build_nativescript_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build NativeScript command"""
        template = 'typescript' if typescript else 'javascript'
        cmd = ['npx', '@nativescript/cli@latest', 'create', name, '--template', template]
        return cmd

    def _build_t3_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build T3 Stack command"""
        cmd = ['npm', 'create', 't3-app@latest', name]
        if pkg_manager != 'npm':
            cmd.extend(['--use-' + pkg_manager])
        return cmd

    def _build_blitz_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build Blitz.js command"""
        cmd = ['npx', 'blitz@latest', 'new', name]
        if typescript:
            cmd.extend(['--template', 'typescript'])
        return cmd

    def _build_redwood_command(self, name: str, typescript: bool, pkg_manager: str) -> list:
        """Build RedwoodJS command"""
        cmd = ['npx', 'create-redwood-app@latest', name]
        if typescript:
            cmd.extend(['--typescript'])
        return cmd

    def _initialize_git(self, project_path: Path):
        """Initialize Git repository"""
        print("\nInitializing Git repository...")
        try:
            use_shell = sys.platform == 'win32'

            subprocess.run(
                ['git', 'init'] if not use_shell else 'git init',
                cwd=project_path,
                check=True,
                capture_output=True,
                shell=use_shell
            )
            subprocess.run(
                ['git', 'add', '.'] if not use_shell else 'git add .',
                cwd=project_path,
                check=True,
                capture_output=True,
                shell=use_shell
            )
            subprocess.run(
                ['git', 'commit', '-m', 'Initial commit'] if not use_shell else 'git commit -m "Initial commit"',
                cwd=project_path,
                check=True,
                capture_output=True,
                shell=use_shell
            )
            print("Git repository initialized")
        except subprocess.CalledProcessError:
            print("  Failed to initialize Git repository")

    def _show_next_steps(self, project_name: str, pkg_manager: str, framework_name: str = ""):
        """Display framework-specific next steps"""
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print(f"\n1. Navigate to your project:")
        print(f"   cd {project_name}")

        # Framework-specific instructions
        if framework_name == "Angular":
            print(f"\n2. Start the development server:")
            print(f"   ng serve")
            print(f"\n3. Open your browser to:")
            print(f"   http://localhost:4200")
        elif framework_name == "React Native":
            print(f"\n2. Install dependencies:")
            print(f"   {pkg_manager} install")
            print(f"\n3. Start Metro bundler:")
            print(f"   npx react-native start")
            print(f"\n4. Run on device/emulator:")
            print(f"   npx react-native run-ios     # For iOS")
            print(f"   npx react-native run-android # For Android")
        elif framework_name == "Expo (React Native)":
            print(f"\n2. Start the Expo development server:")
            print(f"   npx expo start")
            print(f"\n3. Scan QR code with Expo Go app on your phone")
            print(f"   or press 'w' to open in web browser")
        elif "Ionic" in framework_name:
            print(f"\n2. Start the development server:")
            print(f"   ionic serve")
            print(f"\n3. To build for mobile:")
            print(f"   ionic capacitor add ios")
            print(f"   ionic capacitor add android")
            print(f"   ionic capacitor run ios")
        elif framework_name == "Flutter (Web)":
            print(f"\n2. Get dependencies:")
            print(f"   flutter pub get")
            print(f"\n3. Start the development server:")
            print(f"   flutter run -d chrome")
        elif "Capacitor" in framework_name:
            print(f"\n2. Install dependencies:")
            print(f"   {pkg_manager} install")
            print(f"\n3. Add Capacitor:")
            print(f"   npx cap add ios")
            print(f"   npx cap add android")
            print(f"\n4. Build and sync:")
            print(f"   {pkg_manager} run build")
            print(f"   npx cap sync")
        elif framework_name == "NativeScript":
            print(f"\n2. Install dependencies:")
            print(f"   {pkg_manager} install")
            print(f"\n3. Run on device:")
            print(f"   ns run ios")
            print(f"   ns run android")
        elif framework_name in ["Nuxt.js (Vue)", "Remix", "Gatsby"]:
            print(f"\n2. Install dependencies:")
            print(f"   {pkg_manager} install")
            print(f"\n3. Start the development server:")
            print(f"   {pkg_manager} run dev")
            print(f"\n4. Open your browser to:")
            print(f"   http://localhost:3000")
        else:
            # Default web framework instructions
            print(f"\n2. Start the development server:")
            print(f"   {pkg_manager} run dev")
            print(f"\n3. Open your browser to:")
            print(f"   http://localhost:3000")

        # Additional framework-specific tips
        self._show_framework_tips(framework_name)

        print("\n" + "="*70)

    def _show_framework_tips(self, framework_name: str):
        """Show framework-specific tips and resources"""
        tips = {
            "React": [
                "Learn more: https://react.dev/",
                "Useful extensions: React Developer Tools"
            ],
            "Next.js": [
                "Learn more: https://nextjs.org/docs",
                "Deploy easily with Vercel: https://vercel.com/"
            ],
            "Vue.js": [
                "Learn more: https://vuejs.org/guide/",
                "Useful extensions: Vue.js devtools"
            ],
            "Angular": [
                "Learn more: https://angular.io/docs",
                "Use Angular CLI for generators: ng generate component"
            ],
            "React Native": [
                "Learn more: https://reactnative.dev/docs/getting-started",
                "Test on device with Expo Go for quick testing"
            ],
            "Expo (React Native)": [
                "Learn more: https://docs.expo.dev/",
                "Install Expo Go app for easy testing"
            ],
            "Flutter (Web)": [
                "Learn more: https://flutter.dev/docs",
                "Flutter web is great for PWAs"
            ],
            "Svelte": [
                "Learn more: https://svelte.dev/tutorial",
                "Svelte compiles to vanilla JS - no runtime overhead"
            ],
            "Astro": [
                "Learn more: https://docs.astro.build/",
                "Perfect for content-heavy sites with partial hydration"
            ]
        }

        if framework_name in tips:
            print(f"\nTips for {framework_name}:")
            for tip in tips[framework_name]:
                print(f"   {tip}")

    def _prompt_framework(self) -> Optional[str]:
        """Prompt user to select framework category first, then specific framework"""
        # Step 1: Choose category
        category = self._prompt_framework_category()
        if not category:
            return None

        # Step 2: Choose framework from selected category
        return self._prompt_framework_from_category(category)

    def _prompt_framework_category(self) -> Optional[str]:
        """Prompt user to select framework category"""
        categories = [
            "Web Frameworks",
            "Mobile Frameworks",
            "Full-Stack Frameworks",
            "Exit"
        ]

        try:
            choice_idx = get_choice_with_arrows(categories, "Select Framework Category", show_numbers=True)

            # Handle exit option (last option)
            if choice_idx == len(categories):
                print("\nOperation cancelled")
                return None

            # Map choice to category type
            category_map = {
                1: 'web',
                2: 'mobile',
                3: 'fullstack'
            }

            return category_map.get(choice_idx)

        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None

    def _prompt_framework_from_category(self, category: str) -> Optional[str]:
        """Prompt user to select specific framework from chosen category"""
        # Get frameworks for the selected category
        category_frameworks = []
        framework_keys = []

        for key, framework in sorted(self.FRAMEWORKS.items(), key=lambda x: int(x[0])):
            if framework['type'] == category:
                category_frameworks.append(framework['name'])
                framework_keys.append(key)

        if not category_frameworks:
            print(f"No frameworks found for category: {category}")
            return None

        # Add exit option
        category_frameworks.append("Exit")

        try:
            # Get category name for display
            category_names = {
                'web': 'Web',
                'mobile': 'Mobile',
                'fullstack': 'Full-Stack'
            }
            display_name = category_names.get(category, category)

            choice_idx = get_choice_with_arrows(category_frameworks, f"Select {display_name} Framework", show_numbers=True)

            # Handle exit option (last option)
            if choice_idx == len(category_frameworks):
                return None

            # Return the framework key for the selected framework
            return framework_keys[choice_idx - 1]

        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None

    def _prompt_project_name(self) -> Optional[str]:
        """Prompt for project name"""
        while True:
            try:
                name = input("\nProject name (or 'exit' to cancel): ").strip()

                # Handle exit
                if name.lower() in ['exit', 'quit', 'cancel']:
                    print("\nOperation cancelled")
                    return None

                if not name:
                    print("Project name cannot be empty")
                    continue

                if not self._is_valid_project_name(name):
                    print("Invalid project name. Use letters, numbers, hyphens, underscores")
                    continue

                return name

            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return None

    def _prompt_package_manager(self) -> Optional[str]:
        """Prompt for package manager"""
        pm_options = list(self.PACKAGE_MANAGERS.values()) + ["Exit"]

        try:
            choice_idx = get_choice_with_arrows(pm_options, "Package Manager", show_numbers=True)

            # Handle exit option (last option)
            if choice_idx == len(pm_options):
                return None

            # Return the selected package manager directly
            return pm_options[choice_idx - 1]

        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None

    def _prompt_css_framework(self) -> Optional[str]:
        """Prompt for CSS framework"""
        css_options = [value['name'] for value in self.CSS_FRAMEWORKS.values()] + ["Exit"]

        try:
            choice_idx = get_choice_with_arrows(css_options, "CSS Framework", show_numbers=True)

            # Handle exit option (last option)
            if choice_idx == len(css_options):
                return None

            # Find the CSS framework key by matching the selected name
            selected_name = css_options[choice_idx - 1]
            for key, framework in self.CSS_FRAMEWORKS.items():
                if framework['name'] == selected_name:
                    return key

            return '1'  # Default to first option if not found

        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None

    def _prompt_directory(self) -> Optional[str]:
        """Prompt for target directory"""
        try:
            directory = input("\nTarget directory (default: current, or 'exit' to cancel): ").strip()

            # Handle exit
            if directory.lower() in ['exit', 'quit', 'cancel']:
                print("\nOperation cancelled")
                return None

            return directory if directory else '.'
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None

    def _prompt_yes_no(self, question: str, default: str = 'y') -> Optional[bool]:
        """Prompt yes/no question"""
        try:
            default_text = "Y/n" if default == 'y' else "y/N"
            response = input(f"\n{question} [{default_text}] (or 'exit' to cancel): ").strip().lower()

            # Handle exit
            if response in ['exit', 'quit', 'cancel']:
                print("\nOperation cancelled")
                return None

            if not response:
                return default == 'y'

            return response in ['y', 'yes']
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None

    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name"""
        # Allow letters, numbers, hyphens, underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, name))
# Export command instance
COMMAND = CreateFrontendCommand()