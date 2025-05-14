"""
Extremely simple test to verify that our test environment is working
"""
import unittest
import sys
import os

class BasicTest(unittest.TestCase):
    """A very simple test case to verify our test environment is working"""
    
    def test_python_version(self):
        """Test that Python version is at least 3.6"""
        self.assertTrue(sys.version_info.major >= 3)
        self.assertTrue(sys.version_info.minor >= 6)
        print(f"Python version: {sys.version}")
        
    def test_directories(self):
        """Check that critical directories exist"""
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        app_dir = os.path.join(project_dir, 'app')
        test_dir = os.path.join(project_dir, 'test')
        
        self.assertTrue(os.path.exists(app_dir), f"App directory not found: {app_dir}")
        self.assertTrue(os.path.exists(test_dir), f"Test directory not found: {test_dir}")
        
        print(f"Project directory: {project_dir}")
        print(f"App directory exists: {os.path.exists(app_dir)}")
        print(f"Test directory exists: {os.path.exists(test_dir)}")
        
    def test_module_imports(self):
        """Test that we can import critical modules"""
        try:
            import flask
            print(f"Flask version: {flask.__version__}")
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import Flask")
            
        try:
            import selenium
            print(f"Selenium version: {selenium.__version__}")
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import Selenium")

if __name__ == '__main__':
    print("\n=== Running Basic Environment Tests ===\n")
    unittest.main(verbosity=2)
