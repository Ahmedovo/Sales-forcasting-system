import unittest
import sys
import os
import json
from datetime import datetime

# Add backend path to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from app.extensions import db
from app.models import ModelTraining

class ModelTrainingCRUDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create test model training data
        self.test_training = {
            'last_trained_week': 25,
            'last_trained_year': 2023,
            'accuracy': 0.85
        }
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_model_training(self):
        """Test creating a new model training record"""
        response = self.client.post(
            '/api/model-trainings',
            data=json.dumps(self.test_training),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['last_trained_week'], 25)
        self.assertEqual(data['last_trained_year'], 2023)
        self.assertEqual(data['accuracy'], 0.85)
        self.assertIn('id', data)
        
    def test_get_model_training(self):
        """Test retrieving a model training record"""
        # First create a model training record
        training = ModelTraining(
            last_trained_week=self.test_training['last_trained_week'],
            last_trained_year=self.test_training['last_trained_year'],
            accuracy=self.test_training['accuracy']
        )
        db.session.add(training)
        db.session.commit()
        
        # Then retrieve it
        response = self.client.get(f'/api/model-trainings/{training.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['last_trained_week'], 25)
        self.assertEqual(data['last_trained_year'], 2023)
        self.assertEqual(data['accuracy'], 0.85)
        
    def test_get_all_model_trainings(self):
        """Test retrieving all model training records"""
        # Create multiple model training records
        training1 = ModelTraining(last_trained_week=25, last_trained_year=2023, accuracy=0.85)
        training2 = ModelTraining(last_trained_week=26, last_trained_year=2023, accuracy=0.87)
        db.session.add_all([training1, training2])
        db.session.commit()
        
        # Retrieve all model training records
        response = self.client.get('/api/model-trainings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
    def test_update_model_training(self):
        """Test updating a model training record"""
        # First create a model training record
        training = ModelTraining(
            last_trained_week=self.test_training['last_trained_week'],
            last_trained_year=self.test_training['last_trained_year'],
            accuracy=self.test_training['accuracy']
        )
        db.session.add(training)
        db.session.commit()
        
        # Then update it
        update_data = {
            'accuracy': 0.92
        }
        response = self.client.put(
            f'/api/model-trainings/{training.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['accuracy'], 0.92)
        # Other fields should remain unchanged
        self.assertEqual(data['last_trained_week'], 25)
        self.assertEqual(data['last_trained_year'], 2023)
        
    def test_delete_model_training(self):
        """Test deleting a model training record"""
        # First create a model training record
        training = ModelTraining(
            last_trained_week=self.test_training['last_trained_week'],
            last_trained_year=self.test_training['last_trained_year'],
            accuracy=self.test_training['accuracy']
        )
        db.session.add(training)
        db.session.commit()
        
        # Then delete it
        response = self.client.delete(f'/api/model-trainings/{training.id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = self.client.get(f'/api/model-trainings/{training.id}')
        self.assertEqual(response.status_code, 404)
        
    def test_get_latest_model_training(self):
        """Test retrieving the latest model training record"""
        # Create multiple model training records with different dates
        training1 = ModelTraining(last_trained_week=25, last_trained_year=2023, accuracy=0.85)
        training2 = ModelTraining(last_trained_week=26, last_trained_year=2023, accuracy=0.87)
        db.session.add_all([training1, training2])
        db.session.commit()
        
        # Retrieve the latest model training record
        response = self.client.get('/api/model-trainings/latest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['last_trained_week'], 26)
        self.assertEqual(data['last_trained_year'], 2023)
        self.assertEqual(data['accuracy'], 0.87)
        
if __name__ == '__main__':
    unittest.main()