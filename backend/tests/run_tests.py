import unittest
import sys
import os

# Add backend path to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test cases
from tests.test_simple import SimpleTestCase

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases to the suite
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SimpleTestCase))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)