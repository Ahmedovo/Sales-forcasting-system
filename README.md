# Sales Forecasting System

A comprehensive sales forecasting platform that leverages data science and machine learning to predict future sales trends, optimize inventory management, and support business decision-making.

## 🚀 Features

- **Sales Data Management**: Track and manage historical sales data
- **Automated Forecasting**: Weekly sales predictions using machine learning
- **Interactive Dashboard**: Visualize sales trends and forecasts
- **Inventory Optimization**: Recommendations based on predicted demand
- **API Integration**: RESTful API for seamless integration with existing systems

## 🛠️ Technology Stack

### Backend (Flask)

- **Flask**: Lightweight web framework for the API
- **SQLAlchemy**: ORM for database interactions
- **JWT**: Authentication and authorization
- **Scikit-learn**: Machine learning library for forecasting models
- **Pandas & NumPy**: Data manipulation and analysis

### Frontend (React)

- **React**: UI library for building interactive interfaces
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Next-generation frontend tooling

### DevOps

- **Docker**: Containerization for consistent deployment
- **GitHub Actions**: CI/CD pipeline
- **Nginx**: Web server and reverse proxy

## 📊 Data Science Approach

### Forecasting Methodology

The system uses a **Random Forest Regressor** model to predict future sales based on historical data. The forecasting process includes:

1. **Data Preprocessing**: 
   - Time series decomposition
   - Feature engineering (week number, year, etc.)
   - Handling of seasonality and trends

2. **Model Training**:
   - Weekly automated model training
   - Product-specific models for accurate predictions
   - Hyperparameter optimization

3. **Prediction Generation**:
   - Confidence intervals for predictions
   - Multi-week forecasting horizon
   - Accuracy metrics tracking

### Data Engineering Pipeline

1. **Data Collection**: Sales data captured through API endpoints
2. **Data Storage**: Structured in PostgreSQL with optimized schema
3. **ETL Process**: Automated data transformation for model training
4. **Model Persistence**: Trained models saved for future predictions
5. **Scheduled Jobs**: Automated weekly retraining and forecasting

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone [<repository-url>](https://github.com/Ahmedovo/Sales-forcasting-system.git)
   cd 4eme
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🧪 Testing

The backend includes comprehensive test coverage for all CRUD operations and forecasting functionality:

```bash
cd backend
python -m tests.run_tests
```

## 📚 API Documentation

### Authentication

- `POST /auth/login`: Authenticate user and receive JWT token
- `POST /auth/register`: Register new user

### Products

- `GET /products`: List all products
- `POST /products`: Create new product
- `PUT /products`: Update existing product

### Sales

- `GET /sales`: List sales data
- `POST /sales`: Record new sales
- `GET /sales/weekly`: Get weekly sales aggregation

### Forecasts

- `GET /forecast/{product_id}`: Get forecast for specific product
- `GET /forecast/weekly`: Get weekly forecasts for all products
- `POST /forecast/train`: Manually trigger model training

## 🔧 Development

### Backend Development

```bash
cd backend
pip install -r app/requirements.txt
python -m app.app
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 📈 Future Enhancements

- Advanced forecasting models (LSTM, Prophet)
- Anomaly detection in sales patterns
- Automated inventory replenishment recommendations
- Multi-factor forecasting (weather, events, promotions)
