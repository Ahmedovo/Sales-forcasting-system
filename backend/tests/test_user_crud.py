import unittest
import sys
import os
import json
from datetime import datetime

# Add backend path to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from app.extensions import db
from app.models import User

class UserCRUDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create test user
        self.test_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': 'hashed_password'
        }
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_user(self):
        """Test creating a new user"""
        response = self.client.post(
            '/api/users',
            data=json.dumps(self.test_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertIn('id', data)
        
    def test_get_user(self):
        """Test retrieving a user"""
        # First create a user
        user = User(
            username=self.test_user['username'],
            email=self.test_user['email'],
            password_hash=self.test_user['password_hash']
        )
        db.session.add(user)
        db.session.commit()
        
        # Then retrieve it
        response = self.client.get(f'/api/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        
    def test_get_all_users(self):
        """Test retrieving all users"""
        # Create multiple users
        user1 = User(username='user1', email='user1@example.com', password_hash='hash1')
        user2 = User(username='user2', email='user2@example.com', password_hash='hash2')
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Retrieve all users
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
    def test_update_user(self):
        """Test updating a user"""
        # First create a user
        user = User(
            username=self.test_user['username'],
            email=self.test_user['email'],
            password_hash=self.test_user['password_hash']
        )
        db.session.add(user)
        db.session.commit()
        
        # Then update it
        update_data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        response = self.client.put(
            f'/api/users/{user.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'updateduser')
        self.assertEqual(data['email'], 'updated@example.com')
        
    def test_delete_user(self):
        """Test deleting a user"""
        # First create a user
        user = User(
            username=self.test_user['username'],
            email=self.test_user['email'],
            password_hash=self.test_user['password_hash']
        )
        db.session.add(user)
        db.session.commit()
        
        # Then delete it
        response = self.client.delete(f'/api/users/{user.id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = self.client.get(f'/api/users/{user.id}')
        self.assertEqual(response.status_code, 404)
        
    def test_create_duplicate_user(self):
        """Test creating a user with duplicate username or email"""
        # First create a user
        user = User(
            username=self.test_user['username'],
            email=self.test_user['email'],
            password_hash=self.test_user['password_hash']
        )
        db.session.add(user)
        db.session.commit()
        
        # Try to create another user with the same username
        duplicate_user = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password_hash': 'hashed_password'
        }
        response = self.client.post(
            '/api/users',
            data=json.dumps(duplicate_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
if __name__ == '__main__':
    unittest.main()