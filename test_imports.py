"""
Test script to verify that modules can be imported without circular import issues
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that key modules can be imported"""
    print("Testing module imports...")
    
    try:
        print("  - Testing core modules...")
        from core import git_client
        print("    ✓ core.git_client")
        
        from core import security
        print("    ✓ core.security")
        
        from core import config
        print("    ✓ core.config")
        
        from core import exceptions
        print("    ✓ core.exceptions")
        
        print("  - Testing github modules...")
        from github import git_recover
        print("    ✓ github.git_recover")
        
        print("  - Testing dev_mode modules...")
        from dev_mode import docker_quick
        print("    ✓ dev_mode.docker_quick")
        
        print("  - Testing main modules...")
        from git_operations import GitMenu
        print("    ✓ git_operations.GitMenu")
        
        print("  - Testing menu...")
        from menu import MainMenu
        print("    ✓ menu.MainMenu")
        
        print("\n✓ All modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 Import tests passed!")
    else:
        print("\n❌ Import tests failed!")
        sys.exit(1)