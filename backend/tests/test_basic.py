import unittest
import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from app.extensions import db

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
    def tearDown(self):
        self.app_context.pop()
        
    def test_app_exists(self):
        """Test that the app exists"""
        self.assertIsNotNone(self.app)
        
    def test_app_is_testing(self):
        """Test that the app is in testing mode"""
        self.assertTrue(self.app.config['TESTING'])
        
    def test_health_endpoint(self):
        """Test that the health endpoint returns 200"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
if __name__ == '__main__':
    unittest.main()