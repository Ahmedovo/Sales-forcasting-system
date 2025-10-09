import unittest
import sys
import os
import json
from datetime import datetime

# Add backend path to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from app.extensions import db
from app.models import Product, User

class ProductCRUDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create a test user and get JWT token for authentication
        test_user = User(username='testuser', email='test@example.com', password_hash='hashed_password')
        db.session.add(test_user)
        db.session.commit()
        
        # Get JWT token
        response = self.client.post(
            '/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'password'}),
            content_type='application/json'
        )
        if response.status_code == 200:
            self.token = json.loads(response.data)['access_token']
            self.headers = {'Authorization': f'Bearer {self.token}'}
        else:
            # If login fails, create a mock token for testing
            self.headers = {}
        
        # Create test product data
        self.test_product = {
            'sku': 'TEST001',
            'name': 'Test Product',
            'price': 19.99,
            'stock': 100
        }
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_product(self):
        """Test creating a new product"""
        response = self.client.post(
            '/products',
            data=json.dumps(self.test_product),
            content_type='application/json',
            headers=self.headers
        )
        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data)
        self.assertEqual(data['sku'], 'TEST001')
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(data['price'], 19.99)
        self.assertEqual(data['stock'], 100)
        self.assertIn('id', data)
        
    def test_get_all_products(self):
        """Test retrieving all products"""
        # Create multiple products
        product1 = Product(sku='SKU001', name='Product 1', price=10.99, stock=50)
        product2 = Product(sku='SKU002', name='Product 2', price=20.99, stock=75)
        db.session.add_all([product1, product2])
        db.session.commit()
        
        # Retrieve all products
        response = self.client.get('/products', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('items', data)
        self.assertEqual(data['total'], 2)
        
    def test_update_product(self):
        """Test updating a product by creating with same SKU"""
        # First create a product
        product = Product(
            sku=self.test_product['sku'],
            name=self.test_product['name'],
            price=self.test_product['price'],
            stock=self.test_product['stock']
        )
        db.session.add(product)
        db.session.commit()
        
        # Then update it by creating with same SKU (upsert)
        update_data = {
            'sku': 'TEST001',
            'name': 'Updated Product',
            'price': 29.99,
            'stock': 150
        }
        response = self.client.post(
            '/products',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Product')
        self.assertEqual(data['price'], 29.99)
        self.assertEqual(data['stock'], 150)
        self.assertEqual(data['sku'], 'TEST001')
        
    def test_create_duplicate_sku(self):
        """Test creating a product with duplicate SKU (should update)"""
        # First create a product
        product = Product(
            sku=self.test_product['sku'],
            name=self.test_product['name'],
            price=self.test_product['price'],
            stock=self.test_product['stock']
        )
        db.session.add(product)
        db.session.commit()
        
        # Try to create another product with the same SKU (should update)
        duplicate_product = {
            'sku': 'TEST001',
            'name': 'Another Product',
            'price': 15.99,
            'stock': 50
        }
        response = self.client.post(
            '/products',
            data=json.dumps(duplicate_product),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)  # Should be 200 for update
        
if __name__ == '__main__':
    unittest.main()