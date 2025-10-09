import unittest
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SimpleTestCase(unittest.TestCase):
    def test_true(self):
        """Test that True is True"""
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()