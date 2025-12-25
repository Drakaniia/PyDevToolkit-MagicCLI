"""
Documentation Module
Handles automatic documentation generation from code
"""
import sys
import subprocess
import os
from pathlib import Path
import ast
import inspect
from typing import List, Optional, Dict, Any
from core.menu import Menu, MenuItem
from core.security.validator import SecurityValidator


class DocumentationTools:
    """Handles documentation generation tasks"""

    def __init__(self):
        self.validator = SecurityValidator()

    def generate_api_docs(self) -> None:
        """Generate API documentation"""
        print("\n" + "=" * 70)
        print("API DOCUMENTATION GENERATOR")
        print("=" * 70)

        print("\nThis feature would generate API documentation from your code.")
        print("It typically works with frameworks like FastAPI, Flask, or Django.")

        # Look for common API frameworks in the project
        framework_detected = False

        # Check if FastAPI is available and being used
        try:
            import fastapi
            # Look for FastAPI app files
            fastapi_files = list(Path('.').glob('**/*app*.py'))
            for file_path in fastapi_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'FastAPI(' in content:
                        print(f"\n✓ FastAPI detected in {file_path}")
                        framework_detected = True
                        break
        except ImportError:
            pass

        # Check if Flask is available and being used
        if not framework_detected:
            try:
                import flask
                # Look for Flask app files
                flask_files = list(Path('.').glob('**/*app*.py'))
                for file_path in flask_files:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'Flask(' in content:
                            print(f"✓ Flask detected in {file_path}")
                            framework_detected = True
                            break
            except ImportError:
                pass

        if framework_detected:
            print("\nSuggested tools for API documentation:")
            print("  - FastAPI: Automatic docs at /docs and /redoc")
            print("  - Flask: Use Flask-Sphinx for documentation")
            print("  - Django: Use Django REST Framework with drf-yasg")
        else:
            print("\nNo common API frameworks detected.")
            print("API documentation generation depends on the framework used.")

        input("\nPress Enter to continue...")

    def generate_code_docs(self) -> None:
        """Extract and format docstrings from code"""
        print("\n" + "=" * 70)
        print("CODE DOCUMENTATION FROM DOCSTRINGS")
        print("=" * 70)

        print("\nAnalyzing Python files in 'src/' directory for docstrings...")

        # Find Python files in the source directory
        src_path = Path('src')
        if not src_path.exists():
            print("⚠ 'src/' directory not found")
            input("\nPress Enter to continue...")
            return

        python_files = list(src_path.rglob('*.py'))
        print(f"Found {len(python_files)} Python files to analyze")

        # Extract docstrings from files
        docs_summary = {}
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)

                    # Extract module docstring
                    module_docstring = ast.get_docstring(tree)

                    # Extract class and function docstrings
                    classes = []
                    functions = []
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            class_docstring = ast.get_docstring(node)
                            if class_docstring:
                                classes.append({
                                    'name': node.name,
                                    'docstring': class_docstring,
                                    'methods': []
                                })

                                # Extract method docstrings
                                for item in node.body:
                                    if isinstance(item, ast.FunctionDef):
                                        method_docstring = ast.get_docstring(
                                            item)
                                        if method_docstring:
                                            classes[-1]['methods'].append({
                                                'name': item.name,
                                                'docstring': method_docstring
                                            })

                        elif isinstance(node, ast.FunctionDef):
                            func_docstring = ast.get_docstring(node)
                            if func_docstring:
                                functions.append({
                                    'name': node.name,
                                    'docstring': func_docstring
                                })

                    if module_docstring or classes or functions:
                        docs_summary[str(file_path)] = {
                            'module_docstring': module_docstring,
                            'classes': classes,
                            'functions': functions
                        }

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        # Display summary
        print(f"\nFound documentation in {len(docs_summary)} files:")
        for file_path, docs in docs_summary.items():
            print(f"\n  {file_path}:")
            if docs['module_docstring']:
                print("    - Module docstring")
            if docs['classes']:
                print(f"    - {len(docs['classes'])} class docstrings")
            if docs['functions']:
                print(f"    - {len(docs['functions'])} function docstrings")

        # Option to export docs
        if docs_summary:
            response = input(
                "\nWould you like to export the documentation as Markdown? (y/n): ").lower()
            if response == 'y':
                self._export_docs_as_markdown(docs_summary)

        input("\nPress Enter to continue...")

    def _export_docs_as_markdown(self, docs_summary: Dict[str, Any]) -> None:
        """Export documentation as Markdown files"""
        print("\nExporting documentation as Markdown...")

        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Create a main documentation index
        index_content = "# Project Documentation Index\n\n"
        index_content += "This documentation was automatically generated.\n\n"

        for file_path, docs in docs_summary.items():
            # Create a relative path for the documentation file
            doc_file_path = docs_dir / \
                f"{file_path.replace(os.sep, '_').replace('.py', '.md')}"

            content = f"# Documentation for {file_path}\n\n"

            if docs['module_docstring']:
                content += f"## Module Documentation\n\n{docs['module_docstring']}\n\n"

            if docs['classes']:
                content += "## Classes\n\n"
                for class_info in docs['classes']:
                    content += f"### Class: {class_info['name']}\n\n"
                    if class_info['docstring']:
                        content += f"{class_info['docstring']}\n\n"
                    if class_info['methods']:
                        content += "#### Methods:\n\n"
                        for method in class_info['methods']:
                            content += f"- **{method['name']}**: {method['docstring']}\n\n"

            if docs['functions']:
                content += "## Functions\n\n"
                for func in docs['functions']:
                    content += f"### Function: {func['name']}\n\n"
                    if func['docstring']:
                        content += f"{func['docstring']}\n\n"

            # Write to file
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            index_content += f"- [{file_path}]({doc_file_path.name})\n"

        # Write index file
        index_path = docs_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"✓ Documentation exported to '{docs_dir}' directory")
        print(f"  Files created: {len(list(docs_dir.glob('*.md')))}")

    def generate_readme_docs(self) -> None:
        """Enhance or create a README with more details"""
        print("\n" + "=" * 70)
        print("README DOCUMENTATION ENHANCER")
        print("=" * 70)

        readme_path = Path('README.md')
        pyproject_path = Path('pyproject.toml')

        if pyproject_path.exists():
            print("Found pyproject.toml - extracting project information...")

            # Read pyproject.toml to extract project info
            try:
                import tomli  # Requires: pip install tomli
                with open(pyproject_path, 'rb') as f:
                    pyproject_data = tomli.load(f)

                project_info = pyproject_data.get('project', {})
                name = project_info.get('name', 'Project Name')
                description = project_info.get(
                    'description', 'Project description')
                version = project_info.get('version', 'Unknown')
                authors = [
                    author.get(
                        'name',
                        'Unknown') for author in project_info.get(
                        'authors',
                        [])]

                print(f"  Name: {name}")
                print(f"  Description: {description}")
                print(f"  Version: {version}")
                print(f"  Authors: {', '.join(authors)}")

                # Option to update README
                if readme_path.exists():
                    response = input(
                        "\nUpdate README with this information? (y/n): ").lower()
                    if response == 'y':
                        self._update_readme_with_project_info(
                            readme_path, project_info)
                else:
                    response = input(
                        "\nCreate new README with this information? (y/n): ").lower()
                    if response == 'y':
                        self._create_readme_with_project_info(project_info)
            except ImportError:
                print("⚠ tomli package not available. Install with: pip install tomli")
            except Exception as e:
                print(f"⚠ Error reading pyproject.toml: {e}")
        else:
            print("No pyproject.toml found. Manual README enhancement required.")
            print(
                "Consider adding project metadata to pyproject.toml for auto-generation.")

        input("\nPress Enter to continue...")

    def _update_readme_with_project_info(
            self, readme_path: Path, project_info: Dict[str, Any]) -> None:
        """Update existing README with project information"""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the current title (first line)
            lines = content.split('\n')
            title = lines[0] if lines and lines[0].startswith(
                '# ') else f"# {project_info.get('name', 'Project Name')}"

            # Create new content with project info
            new_content = f"{title}\n\n"

            if project_info.get('description'):
                new_content += f"{project_info['description']}\n\n"

            # Add project metadata
            new_content += "## Project Information\n\n"
            if project_info.get('version'):
                new_content += f"- **Version**: {project_info['version']}\n"
            if project_info.get('authors'):
                authors_list = [author['name']
                                for author in project_info['authors']]
                new_content += f"- **Authors**: {', '.join(authors_list)}\n"
            if project_info.get('license'):
                new_content += f"- **License**: {project_info['license']['text']}\n"
            if project_info.get('dependencies'):
                # Limit to first 5
                deps = list(project_info['dependencies'][:5])
                new_content += f"- **Dependencies**: {', '.join(deps)}\n"

            # Add installation instructions
            new_content += "\n## Installation\n\n"
            new_content += "```bash\n"
            new_content += "pip install -e .\n"
            new_content += "```\n\n"

            # Add the rest of the original content
            new_content += "\n" + "\n".join(lines[1:])  # Skip title line

            # Write back to file
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✓ README.md updated with project information")

        except Exception as e:
            print(f"⚠ Error updating README: {e}")

    def _create_readme_with_project_info(
            self, project_info: Dict[str, Any]) -> None:
        """Create a new README with project information"""
        try:
            content = f"# {project_info.get('name', 'Project Name')}\n\n"

            if project_info.get('description'):
                content += f"{project_info['description']}\n\n"

            content += "## Project Information\n\n"
            if project_info.get('version'):
                content += f"- **Version**: {project_info['version']}\n"
            if project_info.get('authors'):
                authors_list = [author['name']
                                for author in project_info['authors']]
                content += f"- **Authors**: {', '.join(authors_list)}\n"
            if project_info.get('license'):
                content += f"- **License**: {project_info['license']['text']}\n"
            if project_info.get('dependencies'):
                # Limit to first 5
                deps = list(project_info['dependencies'][:5])
                content += f"- **Dependencies**: {', '.join(deps)}\n"

            content += "\n## Installation\n\n"
            content += "```bash\n"
            content += "pip install -e .\n"
            content += "```\n\n"

            content += "\n## Features\n\n"
            content += "List of features would go here...\n\n"

            content += "\n## Usage\n\n"
            content += "Usage instructions would go here...\n\n"

            content += "\n## Contributing\n\n"
            content += "Guidelines for contributing would go here...\n\n"

            content += "\n## License\n\n"
            license_text = project_info.get('license', {}).get('text', 'MIT')
            content += f"This project is licensed under the {license_text} License.\n\n"

            # Write to file
            readme_path = Path('README.md')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ README.md created with project information")

        except Exception as e:
            print(f"⚠ Error creating README: {e}")

    def generate_sphinx_docs(self) -> None:
        """Setup Sphinx documentation"""
        print("\n" + "=" * 70)
        print("SPHINX DOCUMENTATION SETUP")
        print("=" * 70)

        try:
            import sphinx
            print("✓ Sphinx is installed")
        except ImportError:
            print("⚠ Sphinx is not installed")
            install = input("Install Sphinx? (y/n): ").lower()
            if install == 'y':
                try:
                    subprocess.run([sys.executable, "-m", "pip",
                                   "install", "sphinx"], check=True)
                    print("✓ Sphinx installed successfully")
                except subprocess.CalledProcessError:
                    print("⚠ Failed to install Sphinx")
                    input("\nPress Enter to continue...")
                    return

        # Create docs directory
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Run sphinx-quickstart
        print("\nSetting up Sphinx documentation structure...")
        sphinx_config_dir = docs_dir / '_build'

        # Create basic conf.py
        import time
        conf_content = f'''# Configuration file for the Sphinx documentation builder.

import os
import sys
import time
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = '{{Path().resolve().name}}'
copyright = '{{time.strftime("%Y")}}, Author'
author = 'Author'

# General configuration
extensions = [
    'sphinx.ext.autodoc',  # Core library for html themes
    'sphinx.ext.viewcode', # Add links to highlighted source code
    'sphinx.ext.napoleon', # Support for NumPy and Google style docstrings
]

templates_path = ['_templates']
exclude_patterns = []

# Options for HTML output
html_theme = 'alabaster'
html_static_path = ['_static']

# Autodoc settings
autodoc_default_options = {{
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}}
'''

        conf_path = docs_dir / 'conf.py'
        with open(conf_path, 'w', encoding='utf-8') as f:
            f.write(conf_content)

        # Create index.rst
        index_content = f'''.. {Path().resolve().name} documentation master file

Welcome to {Path().resolve().name}'s documentation!
=============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''

        index_path = docs_dir / 'index.rst'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"\n✓ Sphinx documentation structure created in '{docs_dir}'")
        print("To build the documentation, run:")
        print(f"  cd {docs_dir}")
        print("  sphinx-build -b html . _build/html")
        print("\nThen open _build/html/index.html in your browser")

        input("\nPress Enter to continue...")


class DocumentationMenu(Menu):
    """Menu for documentation tools"""

    def __init__(self):
        self.documentation = DocumentationTools()
        super().__init__("Documentation Generation Tools")

    def setup_items(self) -> None:
        """Setup menu items for documentation tools"""
        self.items = [
            MenuItem("Generate API Documentation", self.documentation.generate_api_docs),
            MenuItem("Extract Code Documentation", self.documentation.generate_code_docs),
            MenuItem("Enhance README Documentation", self.documentation.generate_readme_docs),
            MenuItem("Setup Sphinx Documentation", self.documentation.generate_sphinx_docs),
            MenuItem("Back to Main Menu", lambda: "exit")
        ]
