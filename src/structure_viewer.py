"""
automation/structure_viewer.py
Enhanced Project Structure Viewer - Excludes Hidden Folders

Features:
- Shows ALL directories with actual source code
- Excludes ALL hidden folders (starting with .) EXCEPT important files
- Respects .gitignore patterns
- Shows only true build artifacts and dependencies as exclusions
- Works across all languages (Python, JavaScript, etc.)
"""
import os
import re
from pathlib import Path
from typing import Set, List, Optional, Tuple


class StructureViewer:
    """Enhanced project structure viewer with hidden folder exclusion"""
    
    # ONLY exclude true build artifacts and dependencies
    EXCLUDE_DIRS = {
        # Python
        "__pycache__", ".pytest_cache", ".mypy_cache", ".tox",
        ".eggs", ".coverage", "htmlcov",
        ".venv", "venv", "env", "ENV", "virtualenv",
        
        # JavaScript/Node
        "node_modules", ".next", ".nuxt", ".cache", ".parcel-cache", 
        ".turbo", "bower_components", "out",
        
        # Build outputs (ONLY generated files)
        "dist", "build", ".build", "target/debug", "target/release",
        
        # Version control (hidden)
        ".git", ".svn", ".hg",
        
        # OS files
        ".DS_Store", "Thumbs.db"
    }
    
    # Exclude directories that match these patterns
    EXCLUDE_DIR_PATTERNS = {
        "*.egg-info",  # Python egg info directories
        "*-info",      # General info directories
        ".coverage*",  # Coverage report directories
    }
    
    # Exclude ONLY generated files
    EXCLUDE_FILES = {
        # Compiled
        "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib",
        "*.class", "*.o", "*.obj",
        
        # Lock files
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "poetry.lock", "Pipfile.lock",
        
        # Minified/compiled assets
        "*.min.js", "*.min.css", "*.map",
        
        # OS
        ".DS_Store", "Thumbs.db", "desktop.ini",
        "*.swp", "*.swo", "*~"
    }
    
    # ALWAYS show these important files (even if hidden)
    ALWAYS_SHOW_FILES = {
        # Environment files
        ".env", ".env.example", ".env.template", ".env.development",
        ".env.local", ".env.production", ".env.test",
        
        # Git files
        ".gitignore", ".dockerignore", ".gitattributes",
        
        # Documentation
        "README.md", "README.txt", "LICENSE", "CHANGELOG.md",
        
        # Docker
        "Dockerfile", "docker-compose.yml", ".dockerignore",
        
        # Code formatting
        ".prettierrc", ".prettierrc.json", ".prettierrc.js", 
        ".prettierrc.yaml", ".prettierignore",
        
        # Linting
        ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yaml",
        ".eslintignore",
        
        # TypeScript/JavaScript config
        "tsconfig.json", "jsconfig.json",
        
        # Package/Project files
        "package.json", "setup.py", "pyproject.toml",
        "requirements.txt", "Cargo.toml", "go.mod",
        
        # Build tools
        "Makefile", ".editorconfig",
        
        # IDE (sometimes important)
        ".vscode/settings.json", ".vscode/launch.json",
        
        # Babel
        ".babelrc", ".babelrc.js", ".babelrc.json"
    }
    
    # Source code extensions (if a directory has these, it's important)
    SOURCE_EXTENSIONS = {
        # Python
        '.py', '.pyx', '.pxd',
        # JavaScript/TypeScript
        '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
        # Vue/React/Svelte
        '.vue', '.svelte',
        # Web
        '.html', '.css', '.scss', '.sass', '.less',
        # Config that might be in folders
        '.json', '.yaml', '.yml', '.toml', '.ini',
        # Other languages
        '.java', '.kt', '.go', '.rs', '.c', '.cpp', '.h', '.hpp',
        '.rb', '.php', '.swift', '.m', '.mm',
        # Scripts
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        # Data/Templates
        '.sql', '.graphql', '.prisma', '.proto',
        '.md', '.rst', '.txt'
    }
    
    def __init__(self, max_depth: int = 8, max_files_per_dir: int = 50):
        """
        Initialize structure viewer
        
        Args:
            max_depth: Maximum directory depth to explore (increased for better deep exploration)
            max_files_per_dir: Maximum files to show per directory (reduced to focus on important files)
        """
        self.current_dir = Path.cwd()
        self.max_depth = max_depth
        self.max_files_per_dir = max_files_per_dir
        self.gitignore_patterns: Set[str] = set()
        
        # Track what's actually being hidden for smart display
        self.hidden_categories = {
            'dependencies': set(),
            'cache': set(),
            'build_artifacts': set(),
            'hidden_folders': set()
        }
        
        # Directories that should show ALL their contents (deep exploration)
        self.IMPORTANT_SOURCE_DIRS = {
            "src", "app", "components", "lib", "utils", "hooks", "pages", 
            "api", "services", "models", "views", "controllers", "routes",
            "config", "constants", "types", "interfaces", "schemas",
            "automation", "tests", "test", "__tests__", "spec",
            "docs", "documentation", "examples", "demo"
        }
    
    def show_structure(self):
        """Display enhanced project structure"""
        self.current_dir = Path.cwd()
        
        print("\n" + "="*70)
        print("📁 PROJECT STRUCTURE")
        print("="*70)
        print(f"\n📍 Current Directory: {self.current_dir.name}")
        print(f"📍 Absolute Path: {self.current_dir.absolute()}")
        
        # Load .gitignore patterns
        self._load_gitignore()
        
        # Reset hidden categories tracking
        self.hidden_categories = {
            'dependencies': set(),
            'cache': set(),
            'build_artifacts': set(),
            'hidden_folders': set()
        }
        
        # Generate the tree structure (this will populate hidden_categories)
        tree_lines = self._generate_tree(self.current_dir)
        
        print("\n💡 Showing: All source code and important files")
        
        # Smart hiding display - only show what's actually being hidden
        hidden_items = []
        if self.hidden_categories['build_artifacts']:
            hidden_items.append("build artifacts")
        if self.hidden_categories['dependencies']:
            hidden_items.append("dependencies")
        if self.hidden_categories['cache']:
            hidden_items.append("cache")
        if self.hidden_categories['hidden_folders']:
            hidden_items.append("hidden folders")
        
        if hidden_items:
            print(f"   Hiding: {', '.join(hidden_items)}")
        
        print(f"   Max depth: {self.max_depth} levels")
        
        # Show summary first for AI context
        file_count, dir_count = self._count_items(self.current_dir)
        print(f"\n📊 Summary: {dir_count} directories, {file_count} files")
        
        print("\n```")
        print(f"{self.current_dir.name}/")
        for line in tree_lines:
            print(line)
        print("```\n")
        
        input("Press Enter to continue...")
    
    def get_clean_structure(self) -> str:
        """
        Get clean structure output optimized for AI consumption
        Returns the structure as a simple string without UI elements
        """
        self.current_dir = Path.cwd()
        self._load_gitignore()
        
        # Reset hidden categories tracking
        self.hidden_categories = {
            'dependencies': set(),
            'cache': set(),
            'build_artifacts': set(),
            'hidden_folders': set()
        }
        
        # Generate the tree structure
        tree_lines = self._generate_tree(self.current_dir)
        
        # Build clean output
        output_lines = [f"{self.current_dir.name}/"]
        output_lines.extend(tree_lines)
        
        return "\n".join(output_lines)
    
    def _load_gitignore(self):
        """Load and parse .gitignore patterns"""
        gitignore_path = self.current_dir / ".gitignore"
        
        if not gitignore_path.exists():
            return
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Store pattern
                    self.gitignore_patterns.add(line)
        
        except Exception:
            pass
    
    def _should_exclude(self, path: Path, is_dir: bool = False) -> bool:
        """
        Determine if path should be excluded

        Enhanced Strategy:
        1. NEVER exclude if it's an ALWAYS_SHOW file
        2. ALWAYS exclude hidden folders (starting with .) UNLESS they contain only important files
        3. NEVER exclude non-hidden directories with source code (including deep nested ones)
        4. ONLY exclude if it's in EXCLUDE_DIRS/FILES or .gitignore

        Args:
            path: Path to check
            is_dir: Whether it's a directory

        Returns:
            True if should be excluded
        """
        # Validate path for security (check for path traversal)
        try:
            # Resolve path to prevent directory traversal
            resolved_path = path.resolve()
            # Ensure the path is within the current directory
            resolved_path.relative_to(self.current_dir.resolve())
        except ValueError:
            # Path is outside the current directory, exclude it for security
            return True

        name = path.name
        
        # Rule 1: Never exclude always-show files
        if not is_dir and name in self.ALWAYS_SHOW_FILES:
            return False
        
        # Also check relative path for nested important files (like .vscode/settings.json)
        try:
            relative_path = str(path.relative_to(self.current_dir))
            if relative_path in self.ALWAYS_SHOW_FILES:
                return False
        except ValueError:
            pass
        
        # Rule 2: ALWAYS exclude hidden folders (starting with .)
        # Exception: Only if it's an important config file
        if name.startswith('.'):
            if is_dir:
                # Hidden directory - ALWAYS exclude
                # Exception: Check if it's a special case like .vscode with important files
                if name == '.vscode':
                    # Only show .vscode if it has important files
                    should_exclude = not self._has_important_vscode_files(path)
                    if should_exclude:
                        self.hidden_categories['hidden_folders'].add(name)
                    return should_exclude
                
                # All other hidden directories are excluded
                self.hidden_categories['hidden_folders'].add(name)
                return True
            else:
                # Hidden file - only show if in ALWAYS_SHOW_FILES
                should_exclude = name not in self.ALWAYS_SHOW_FILES
                if should_exclude:
                    self.hidden_categories['hidden_folders'].add(name)
                return should_exclude
        
        # Rule 3: Check explicit exclude lists BEFORE source code check
        # This ensures build artifacts are always excluded
        if is_dir:
            if name in self.EXCLUDE_DIRS:
                # Categorize the exclusion
                if name in {'node_modules', 'bower_components'}:
                    self.hidden_categories['dependencies'].add(name)
                elif name in {'__pycache__', '.pytest_cache', '.mypy_cache', '.cache', '.parcel-cache', '.turbo'}:
                    self.hidden_categories['cache'].add(name)
                elif name in {'dist', 'build', '.build', 'target/debug', 'target/release', 'out'}:
                    self.hidden_categories['build_artifacts'].add(name)
                elif name in {'.venv', 'venv', 'env', 'ENV', 'virtualenv'}:
                    self.hidden_categories['dependencies'].add(name)
                else:
                    self.hidden_categories['hidden_folders'].add(name)
                return True
            # Check directory patterns
            for pattern in self.EXCLUDE_DIR_PATTERNS:
                if self._matches_pattern(name, pattern):
                    if 'egg-info' in pattern or 'info' in pattern:
                        self.hidden_categories['build_artifacts'].add(name)
                    elif 'coverage' in pattern:
                        self.hidden_categories['cache'].add(name)
                    else:
                        self.hidden_categories['build_artifacts'].add(name)
                    return True
        
        # Rule 3.5: For directories, check if they contain source code
        # This ensures we show important directories that aren't explicitly excluded
        if is_dir and not name.startswith('.'):
            # Check if this directory or its subdirectories contain source code
            if self._has_source_code_deep(path):
                return False
        
        # Rule 4: Check file exclusion patterns
        if not is_dir:
            for pattern in self.EXCLUDE_FILES:
                if self._matches_pattern(name, pattern):
                    if pattern in {'*.pyc', '*.pyo', '*.pyd', '*.class', '*.o', '*.obj'}:
                        self.hidden_categories['build_artifacts'].add(name)
                    elif pattern in {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'Pipfile.lock'}:
                        self.hidden_categories['dependencies'].add(name)
                    elif pattern in {'*.min.js', '*.min.css', '*.map'}:
                        self.hidden_categories['build_artifacts'].add(name)
                    else:
                        self.hidden_categories['cache'].add(name)
                    return True
        
        # Rule 5: Check .gitignore
        try:
            relative_path = str(path.relative_to(self.current_dir))
            for pattern in self.gitignore_patterns:
                if self._matches_gitignore(relative_path, pattern, is_dir):
                    # For directories, double-check if they contain source code
                    if is_dir and not name.startswith('.') and self._has_source_code_deep(path):
                        return False
                    # Track gitignore exclusions as build artifacts (most common case)
                    self.hidden_categories['build_artifacts'].add(name)
                    return True
        except ValueError:
            pass
        
        return False
    
    def _has_important_vscode_files(self, vscode_dir: Path) -> bool:
        """
        Check if .vscode directory contains important config files
        
        Args:
            vscode_dir: .vscode directory path
        
        Returns:
            True if contains important files
        """
        important_vscode_files = {'settings.json', 'launch.json', 'tasks.json'}
        
        try:
            for item in vscode_dir.iterdir():
                if item.is_file() and item.name in important_vscode_files:
                    return True
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _has_source_code(self, directory: Path) -> bool:
        """
        Check if directory contains actual source code files
        
        Args:
            directory: Directory to check
        
        Returns:
            True if contains source files
        """
        try:
            # Quick check: look at immediate children
            for item in directory.iterdir():
                if item.is_file():
                    # Check if it's a source file
                    if item.suffix in self.SOURCE_EXTENSIONS:
                        return True
                    # Check if it's an important file
                    if item.name in self.ALWAYS_SHOW_FILES:
                        return True
                elif item.is_dir() and not item.name.startswith('.'):
                    # Recursively check subdirectories (but limit depth)
                    if self._has_source_code_shallow(item):
                        return True
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _has_source_code_shallow(self, directory: Path, depth: int = 0) -> bool:
        """Shallow recursive check for source code (max 2 levels deep)"""
        if depth > 1:
            return False
        
        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix in self.SOURCE_EXTENSIONS:
                    return True
                elif item.is_dir() and not item.name.startswith('.'):
                    if self._has_source_code_shallow(item, depth + 1):
                        return True
        except (PermissionError, OSError):
            pass
        
        return False
    
    def _has_source_code_deep(self, directory: Path, depth: int = 0) -> bool:
        """
        Deep recursive check for source code with more thorough scanning
        This is used to ensure important directories like src/app are never hidden

        Args:
            directory: Directory to check
            depth: Current recursion depth

        Returns:
            True if directory or any subdirectory contains source files
        """
        # Prevent infinite recursion and limit depth for performance
        if depth > 4:  # Allow deeper checking than shallow version
            return False

        try:
            # Use scandir for better performance when available (Python 3.5+)
            # This is faster than iterdir() for directories with many files
            with os.scandir(directory) as entries:
                for entry in entries:
                    # Use entry methods to avoid extra stat calls
                    if entry.is_file():
                        # Check if it's a source file
                        if Path(entry.name).suffix in self.SOURCE_EXTENSIONS:
                            return True
                        # Check if it's an important file
                        if entry.name in self.ALWAYS_SHOW_FILES:
                            return True
                    elif entry.is_dir():
                        # Skip hidden directories and known excluded directories
                        if entry.name.startswith('.') or entry.name in self.EXCLUDE_DIRS:
                            continue
                        # Recursively check subdirectories
                        if self._has_source_code_deep(Path(entry.path), depth + 1):
                            return True
        except (PermissionError, OSError, FileNotFoundError):
            pass

        return False
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Check if name matches wildcard pattern"""
        pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
        return bool(re.match(f'^{pattern_regex}$', name))
    
    def _matches_gitignore(self, path: str, pattern: str, is_dir: bool) -> bool:
        """Check if path matches .gitignore pattern"""
        # Handle trailing slash (directory-only patterns)
        if pattern.endswith('/'):
            if not is_dir:
                return False
            pattern = pattern[:-1]
        
        # Handle leading slash (root-relative patterns)
        if pattern.startswith('/'):
            pattern = pattern[1:]
            return path == pattern or path.startswith(pattern + '/')
        
        # Handle wildcards
        if '*' in pattern:
            pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
            return bool(re.search(pattern_regex, path))
        
        # Simple substring match
        path_parts = path.split('/')
        return pattern in path_parts or path.endswith('/' + pattern)
    
    def _generate_tree(
        self,
        directory: Path,
        prefix: str = "",
        depth: int = 0
    ) -> List[str]:
        """
        Generate tree structure with enhanced sorting and prioritization
        
        Args:
            directory: Directory to scan
            prefix: Prefix for tree lines
            depth: Current depth level
        
        Returns:
            List of tree lines
        """
        if depth >= self.max_depth:
            return []
        
        lines = []
        
        try:
            # Get all items
            items = list(directory.iterdir())
            
            # Filter out excluded items
            filtered_items = []
            for item in items:
                if not self._should_exclude(item, item.is_dir()):
                    filtered_items.append(item)
            
            # Enhanced sorting for better AI understanding
            def sort_key(item: Path):
                name = item.name.lower()
                is_dir = item.is_dir()
                
                # Priority order for better structure presentation
                priority = 0
                
                # Highest priority: important config files
                if name in {'readme.md', 'package.json', 'setup.py', 'requirements.txt', 'dockerfile'}:
                    priority = 1
                # High priority: source directories
                elif is_dir and name in self.IMPORTANT_SOURCE_DIRS:
                    priority = 2
                # Medium priority: other directories
                elif is_dir:
                    priority = 3
                # Lower priority: source files
                elif any(name.endswith(ext) for ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue']):
                    priority = 4
                # Lowest priority: other files
                else:
                    priority = 5
                
                return (priority, name)
            
            filtered_items.sort(key=sort_key)
            
            # Smart limiting based on directory importance
            current_dir_name = directory.name.lower()
            is_important_dir = current_dir_name in self.IMPORTANT_SOURCE_DIRS
            
            if is_important_dir:
                # Show more items in important directories
                max_items = min(self.max_files_per_dir * 2, 100)
            else:
                max_items = self.max_files_per_dir
            
            if len(filtered_items) > max_items:
                shown_items = filtered_items[:max_items]
                hidden_count = len(filtered_items) - max_items
            else:
                shown_items = filtered_items
                hidden_count = 0
            
            # Generate lines for each item
            for i, item in enumerate(shown_items):
                is_last = (i == len(shown_items) - 1) and (hidden_count == 0)
                
                # Tree characters
                if is_last:
                    current_prefix = "└── "
                    next_prefix = "    "
                else:
                    current_prefix = "├── "
                    next_prefix = "│   "
                
                # Display name with size for files (optimized for AI readability)
                if item.is_dir():
                    display_name = f"{item.name}/"
                else:
                    try:
                        size = self._format_size(item.stat().st_size)
                        # Only show size for larger files to reduce noise
                        if item.stat().st_size > 1024:  # Show size for files > 1KB
                            display_name = f"{item.name} ({size})"
                        else:
                            display_name = item.name
                    except:
                        display_name = item.name
                
                lines.append(f"{prefix}{current_prefix}{display_name}")
                
                # Recurse into subdirectories
                if item.is_dir():
                    sublines = self._generate_tree(
                        item,
                        prefix + next_prefix,
                        depth + 1
                    )
                    lines.extend(sublines)
            
            # Show hidden count if any
            if hidden_count > 0:
                lines.append(f"{prefix}└── ... and {hidden_count} more items")
        
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
        except Exception as e:
            lines.append(f"{prefix}[Error: {str(e)[:30]}]")
        
        return lines
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def _count_items(self, directory: Path) -> Tuple[int, int]:
        """
        Count files and directories recursively
        
        Returns:
            Tuple of (file_count, dir_count)
        """
        file_count = 0
        dir_count = 0
        
        def count_recursive(path: Path, depth: int):
            nonlocal file_count, dir_count
            
            if depth > self.max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if self._should_exclude(item, item.is_dir()):
                        continue
                    
                    if item.is_file():
                        file_count += 1
                    elif item.is_dir():
                        dir_count += 1
                        count_recursive(item, depth + 1)
            except (PermissionError, OSError):
                pass
        
        count_recursive(directory, 0)
        return file_count, dir_count


# Test
if __name__ == "__main__":
    viewer = StructureViewer(max_depth=5)
    viewer.show_structure()