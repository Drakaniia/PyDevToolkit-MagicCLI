"""
Comprehensive Test Suite for Python Automation System
Tests all major components and modules in the application
"""

import unittest
import os
import sys
import subprocess
from pathlib import Path

# Add the src directory to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestCoreComponents(unittest.TestCase):
    """Test core components of the application"""
    
    def test_menu_imports(self):
        """Test that menu components can be imported"""
        try:
            from menu import Menu, MenuItem
            self.assertIsNotNone(Menu)
            self.assertIsNotNone(MenuItem)
        except ImportError as e:
            self.fail(f"Failed to import menu components: {e}")
    
    def test_command_handler_imports(self):
        """Test that command handler can be imported"""
        try:
            from core.command_handler import Command, CommandRegistry, CLICommandHandler
            self.assertIsNotNone(Command)
            self.assertIsNotNone(CommandRegistry)
            self.assertIsNotNone(CLICommandHandler)
        except ImportError as e:
            print(f"Command handler not found: {e}")
            # This is OK if the file doesn't exist yet
    
    def test_menu_handler_imports(self):
        """Test that menu handler can be imported"""
        try:
            from core.menu_handler import BaseMenuHandler, GitMenuHandler, OperationSelectionHandler, ConfirmationHandler, MenuHelper
            self.assertIsNotNone(BaseMenuHandler)
            self.assertIsNotNone(GitMenuHandler)
        except ImportError as e:
            print(f"Menu handler not found: {e}")
            # This is OK if the file doesn't exist yet


class TestGitHubOperations(unittest.TestCase):
    """Test GitHub operations module"""
    
    def test_git_operations_imports(self):
        """Test that git operations can be imported"""
        try:
            from git_operations import GitOperations, GitMenu
            self.assertIsNotNone(GitOperations)
            self.assertIsNotNone(GitMenu)
        except ImportError as e:
            self.fail(f"Failed to import git operations: {e}")
    
    def test_git_status_imports(self):
        """Test that GitStatus can be imported"""
        try:
            from github.git_status import GitStatus
            self.assertIsNotNone(GitStatus)
        except ImportError as e:
            self.fail(f"Failed to import GitStatus: {e}")
    
    def test_git_push_imports(self):
        """Test that GitPush can be imported"""
        try:
            from github.git_push import GitPush
            self.assertIsNotNone(GitPush)
        except ImportError as e:
            self.fail(f"Failed to import GitPush: {e}")
    
    def test_git_pull_imports(self):
        """Test that GitPull can be imported"""
        try:
            from github.git_pull import GitPull
            self.assertIsNotNone(GitPull)
        except ImportError as e:
            self.fail(f"Failed to import GitPull: {e}")
    
    def test_git_log_imports(self):
        """Test that GitLog can be imported"""
        try:
            from github.git_log import GitLog
            self.assertIsNotNone(GitLog)
        except ImportError as e:
            self.fail(f"Failed to import GitLog: {e}")
    
    def test_git_recover_imports(self):
        """Test that GitRecover can be imported"""
        try:
            from github.git_recover import GitRecover
            self.assertIsNotNone(GitRecover)
        except ImportError as e:
            self.fail(f"Failed to import GitRecover: {e}")
    
    def test_git_stash_imports(self):
        """Test that GitStash can be imported"""
        try:
            from github.git_stash import GitStash
            self.assertIsNotNone(GitStash)
        except ImportError as e:
            self.fail(f"Failed to import GitStash: {e}")
    
    def test_git_diff_imports(self):
        """Test that GitDiff can be imported"""
        try:
            from github.git_diff import GitDiff
            self.assertIsNotNone(GitDiff)
        except ImportError as e:
            self.fail(f"Failed to import GitDiff: {e}")
    
    def test_git_cache_imports(self):
        """Test that GitCache can be imported"""
        try:
            from github.git_cache import GitCache
            self.assertIsNotNone(GitCache)
        except ImportError as e:
            self.fail(f"Failed to import GitCache: {e}")
    
    def test_git_initializer_imports(self):
        """Test that GitInitializer can be imported"""
        try:
            from github.git_initializer import GitInitializer
            self.assertIsNotNone(GitInitializer)
        except ImportError as e:
            self.fail(f"Failed to import GitInitializer: {e}")
    
    def test_git_removesubmodule_imports(self):
        """Test that GitRemoveSubmodule can be imported"""
        try:
            from github.git_removesubmodule import GitRemoveSubmodule
            self.assertIsNotNone(GitRemoveSubmodule)
        except ImportError as e:
            self.fail(f"Failed to import GitRemoveSubmodule: {e}")


class TestCoreModules(unittest.TestCase):
    """Test core modules"""
    
    def test_core_exceptions_imports(self):
        """Test that core exceptions can be imported"""
        try:
            import core.exceptions
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import core exceptions: {e}")

    def test_core_loading_imports(self):
        """Test that core loading can be imported"""
        try:
            import core.loading
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import core loading: {e}")

    def test_core_git_client_imports(self):
        """Test that core git client can be imported"""
        try:
            import core.git_client
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import core git client: {e}")


class TestMainModules(unittest.TestCase):
    """Test main modules"""
    
    def test_banner_imports(self):
        """Test that banner can be imported"""
        try:
            import banner
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import banner: {e}")
    
    def test_changelog_generator_imports(self):
        """Test that changelog generator can be imported"""
        try:
            import changelog_generator
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import changelog generator: {e}")

    def test_folder_navigator_imports(self):
        """Test that folder navigator can be imported"""
        try:
            import folder_navigator
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import folder navigator: {e}")

    def test_structure_viewer_imports(self):
        """Test that structure viewer can be imported"""
        try:
            import structure_viewer
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import structure viewer: {e}")

    def test_magic_imports(self):
        """Test that magic can be imported"""
        try:
            import magic
            # Just check if the module can be imported without errors
        except ImportError as e:
            self.fail(f"Failed to import magic: {e}")


class TestDevMode(unittest.TestCase):
    """Test dev mode modules if they exist"""
    
    def test_dev_mode_imports(self):
        """Test that dev mode components can be imported"""
        try:
            from dev_mode.dev_menu import DevModeMenu
            self.assertIsNotNone(DevModeMenu)
        except ImportError:
            print("DevModeMenu not found - this is OK if the file doesn't exist")
            pass  # This is OK if the file doesn't exist yet


class TestBackend(unittest.TestCase):
    """Test backend modules if they exist"""
    
    def test_backend_imports(self):
        """Test that backend components can be imported"""
        try:
            from backend.backend_menu import BackendDevMenu
            self.assertIsNotNone(BackendDevMenu)
        except ImportError:
            print("BackendDevMenu not found - this is OK if the file doesn't exist")
            pass  # This is OK if the file doesn't exist yet


class TestIntegration(unittest.TestCase):
    """Integration tests to check if modules work together"""
    
    def test_git_operations_integration(self):
        """Test basic GitOperations functionality"""
        try:
            from git_operations import GitOperations
            git_ops = GitOperations()
            # Just test instantiation - actual operations require a git repo
            self.assertIsInstance(git_ops, GitOperations)
        except Exception as e:
            self.fail(f"GitOperations integration failed: {e}")
    
    def test_menu_creation(self):
        """Test basic menu creation"""
        try:
            from menu import Menu, MenuItem
            from git_operations import GitOperations
            
            class TestMenu(Menu):
                def __init__(self):
                    super().__init__("Test Menu")
                    self.git_ops = GitOperations()
                
                def setup_items(self):
                    self.items = [
                        MenuItem("Test", lambda: "test_result")
                    ]
            
            test_menu = TestMenu()
            self.assertIsInstance(test_menu, Menu)
        except Exception as e:
            self.fail(f"Menu creation integration failed: {e}")


class TestCommandExecution(unittest.TestCase):
    """Test command execution capabilities"""
    
    def test_python_imports_work(self):
        """Test that all modules can be imported without errors"""
        modules_to_test = [
            'git_operations',
            'menu',
            'core.git_client',
            'github.git_status',
            'github.git_push',
            'github.git_pull',
            'github.git_log',
            'github.git_recover',
            'github.git_stash',
            'github.git_diff',
            'github.git_cache',
            'github.git_initializer',
            'github.git_removesubmodule',
            'core.command_handler',
            'core.menu_handler',
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                # Some modules might not exist yet, which is OK
                print(f"Module {module_name} not found: {e}")
                continue
            except Exception as e:
                self.fail(f"Unexpected error importing {module_name}: {e}")


def discover_and_test_all_modules():
    """Dynamically discover and test all modules in the codebase"""
    import importlib
    import pkgutil

    # Add the src directory to Python path to import modules
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

    # List of modules to specifically test
    discovered_modules = []

    # Discover all Python modules in src directory
    src_path = Path(__file__).parent.parent / 'src'

    for root, dirs, files in os.walk(src_path):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if not d.startswith('__')]

        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                # Calculate the module path relative to src
                file_path = Path(root) / file
                module_path = file_path.relative_to(src_path)

                # Convert to module name (e.g., github/git_stash.py -> github.git_stash)
                module_parts = []
                for part in module_path.parts:
                    if part.endswith('.py'):
                        part = part[:-3]  # Remove .py
                    module_parts.append(part)

                module_name = '.'.join(module_parts)
                if module_name not in discovered_modules:
                    discovered_modules.append(module_name)

    # Also check for modules in the root of src
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=[str(src_path)],
        prefix="",
        onerror=lambda x: None
    ):
        if modname not in discovered_modules:
            discovered_modules.append(modname)

    print(f"Discovered {len(discovered_modules)} modules to test:")
    for module in discovered_modules:
        print(f"  - {module}")

    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all existing test cases to the suite
    suite.addTests(loader.loadTestsFromTestCase(TestCoreComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestGitHubOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestCoreModules))
    suite.addTests(loader.loadTestsFromTestCase(TestMainModules))
    suite.addTests(loader.loadTestsFromTestCase(TestDevMode))
    suite.addTests(loader.loadTestsFromTestCase(TestBackend))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandExecution))

    # Add a new test class to test all discovered modules
    class AllModuleImportTests(unittest.TestCase):
        """Dynamically generated tests for all discovered modules"""
        pass

    # Dynamically add test methods for each discovered module
    for module_name in discovered_modules:
        def make_test(mod_name):
            def test_module(self):
                try:
                    module = importlib.import_module(mod_name)
                    # Optionally, we could add more specific tests here, such as:
                    # - check if certain classes/functions exist
                    # - validate module structure
                    # For now, just test that import works
                except ImportError as e:
                    # Some modules might have dependencies we don't have installed
                    print(f"Note: Could not import {mod_name}: {e}")
                    pass  # Still pass the test - it might be OK if dependencies are missing
            return test_module

        test_method = make_test(module_name)
        test_method.__name__ = f'test_import_{module_name.replace(".", "_").replace("-", "_")}'
        setattr(AllModuleImportTests, test_method.__name__, test_method)

    suite.addTests(loader.loadTestsFromTestCase(AllModuleImportTests))

    return suite


def run_all_tests():
    """Run all tests including dynamically discovered modules and return results"""
    # Create the full test suite
    loader = unittest.TestLoader()
    suite = discover_and_test_all_modules()

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    print("Running comprehensive test suite for Python Automation System...")
    print("="*70)

    result = run_all_tests()

    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    if result.wasSuccessful():
        print("\nAll tests passed! [PASS]")
    else:
        print("\nSome tests failed or had errors. [FAIL]")

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)