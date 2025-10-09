import unittest
import sys
import os
import json
from datetime import datetime, date

# Add backend path to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.app import create_app
from app.extensions import db
from app.models import Product, Sale, Forecast, User

class SaleForecastCRUDTestCase(unittest.TestCase):
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
        
        # Create a test product first
        self.test_product = Product(
            sku='TEST001',
            name='Test Product',
            price=19.99,
            stock=100
        )
        db.session.add(self.test_product)
        db.session.commit()
        
        # Create test sale data
        self.test_sale = {
            'product_id': self.test_product.id,
            'quantity': 5,
            'total_price': 99.95,
            'week_number': 25,
            'year': 2023
        }
        
        # Create test forecast data
        self.test_forecast = {
            'product_id': self.test_product.id,
            'predicted_quantity': 10.5,
            'lower_bound': 8.2,
            'upper_bound': 12.8,
            'forecast_date': '2023-07-01',
            'week_number': 26,
            'year': 2023
        }
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    # Sale CRUD Tests
    def test_create_sale(self):
        """Test creating a new sale"""
        response = self.client.post(
            '/sales',
            data=json.dumps(self.test_sale),
            content_type='application/json',
            headers=self.headers
        )
        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data)
        # Verify the response contains the expected data
        # Adjust assertions based on actual API response structure
        self.assertTrue(isinstance(data, dict))
        
    def test_get_sale(self):
        """Test retrieving a sale"""
        # First create a sale
        sale = Sale(
            product_id=self.test_product.id,
            quantity=self.test_sale['quantity'],
            total_price=self.test_sale['total_price'],
            week_number=self.test_sale['week_number'],
            year=self.test_sale['year']
        )
        db.session.add(sale)
        db.session.commit()
        
        # Then retrieve it
        response = self.client.get(f'/api/sales/{sale.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['product_id'], self.test_product.id)
        self.assertEqual(data['quantity'], 5)
        
    def test_get_all_sales(self):
        """Test retrieving all sales"""
        # Create multiple sales
        sale1 = Sale(product_id=self.test_product.id, quantity=5, total_price=99.95, week_number=25, year=2023)
        sale2 = Sale(product_id=self.test_product.id, quantity=3, total_price=59.97, week_number=26, year=2023)
        db.session.add_all([sale1, sale2])
        db.session.commit()
        
        # Retrieve all sales
        response = self.client.get('/api/sales')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
    def test_update_sale(self):
        """Test updating a sale"""
        # First create a sale
        sale = Sale(
            product_id=self.test_product.id,
            quantity=self.test_sale['quantity'],
            total_price=self.test_sale['total_price'],
            week_number=self.test_sale['week_number'],
            year=self.test_sale['year']
        )
        db.session.add(sale)
        db.session.commit()
        
        # Then update it
        update_data = {
            'quantity': 8,
            'total_price': 159.92
        }
        response = self.client.put(
            f'/api/sales/{sale.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['quantity'], 8)
        self.assertEqual(data['total_price'], 159.92)
        
    def test_delete_sale(self):
        """Test deleting a sale"""
        # First create a sale
        sale = Sale(
            product_id=self.test_product.id,
            quantity=self.test_sale['quantity'],
            total_price=self.test_sale['total_price'],
            week_number=self.test_sale['week_number'],
            year=self.test_sale['year']
        )
        db.session.add(sale)
        db.session.commit()
        
        # Then delete it
        response = self.client.delete(f'/api/sales/{sale.id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = self.client.get(f'/api/sales/{sale.id}')
        self.assertEqual(response.status_code, 404)
    
    # Forecast CRUD Tests
    def test_create_forecast(self):
        """Test creating a new forecast"""
        response = self.client.post(
            '/api/forecasts',
            data=json.dumps(self.test_forecast),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['product_id'], self.test_product.id)
        self.assertEqual(data['predicted_quantity'], 10.5)
        self.assertEqual(data['lower_bound'], 8.2)
        self.assertEqual(data['upper_bound'], 12.8)
        self.assertEqual(data['week_number'], 26)
        self.assertEqual(data['year'], 2023)
        self.assertIn('id', data)
        
    def test_get_forecast(self):
        """Test retrieving a forecast"""
        # First create a forecast
        forecast = Forecast(
            product_id=self.test_product.id,
            predicted_quantity=self.test_forecast['predicted_quantity'],
            lower_bound=self.test_forecast['lower_bound'],
            upper_bound=self.test_forecast['upper_bound'],
            forecast_date=date.fromisoformat(self.test_forecast['forecast_date']),
            week_number=self.test_forecast['week_number'],
            year=self.test_forecast['year']
        )
        db.session.add(forecast)
        db.session.commit()
        
        # Then retrieve it
        response = self.client.get(f'/api/forecasts/{forecast.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['product_id'], self.test_product.id)
        self.assertEqual(data['predicted_quantity'], 10.5)
        
    def test_get_all_forecasts(self):
        """Test retrieving all forecasts"""
        # Create multiple forecasts
        forecast1 = Forecast(
            product_id=self.test_product.id, 
            predicted_quantity=10.5, 
            lower_bound=8.2, 
            upper_bound=12.8, 
            forecast_date=date(2023, 7, 1),
            week_number=26, 
            year=2023
        )
        forecast2 = Forecast(
            product_id=self.test_product.id, 
            predicted_quantity=12.0, 
            lower_bound=9.5, 
            upper_bound=14.5, 
            forecast_date=date(2023, 7, 8),
            week_number=27, 
            year=2023
        )
        db.session.add_all([forecast1, forecast2])
        db.session.commit()
        
        # Retrieve all forecasts
        response = self.client.get('/api/forecasts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
    def test_update_forecast(self):
        """Test updating a forecast"""
        # First create a forecast
        forecast = Forecast(
            product_id=self.test_product.id,
            predicted_quantity=self.test_forecast['predicted_quantity'],
            lower_bound=self.test_forecast['lower_bound'],
            upper_bound=self.test_forecast['upper_bound'],
            forecast_date=date.fromisoformat(self.test_forecast['forecast_date']),
            week_number=self.test_forecast['week_number'],
            year=self.test_forecast['year']
        )
        db.session.add(forecast)
        db.session.commit()
        
        # Then update it
        update_data = {
            'predicted_quantity': 15.0,
            'lower_bound': 12.5,
            'upper_bound': 17.5
        }
        response = self.client.put(
            f'/api/forecasts/{forecast.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['predicted_quantity'], 15.0)
        self.assertEqual(data['lower_bound'], 12.5)
        self.assertEqual(data['upper_bound'], 17.5)
        
    def test_delete_forecast(self):
        """Test deleting a forecast"""
        # First create a forecast
        forecast = Forecast(
            product_id=self.test_product.id,
            predicted_quantity=self.test_forecast['predicted_quantity'],
            lower_bound=self.test_forecast['lower_bound'],
            upper_bound=self.test_forecast['upper_bound'],
            forecast_date=date.fromisoformat(self.test_forecast['forecast_date']),
            week_number=self.test_forecast['week_number'],
            year=self.test_forecast['year']
        )
        db.session.add(forecast)
        db.session.commit()
        
        # Then delete it
        response = self.client.delete(f'/api/forecasts/{forecast.id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = self.client.get(f'/api/forecasts/{forecast.id}')
        self.assertEqual(response.status_code, 404)
        
if __name__ == '__main__':
    unittest.main()