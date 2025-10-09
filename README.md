# Système de Prévision des Ventes et Gestion de Stock
# Sales Forecasting and Inventory Management System

## Français

Ce projet est une application complète de prévision des ventes et de gestion de stock qui intègre:
- Un backend développé avec Flask et PostgreSQL
- Une interface utilisateur réactive construite avec React et TypeScript
- Un système d'ingénierie de données (ETL) pour le traitement des données
- Des modèles d'apprentissage automatique pour la prévision des ventes

### Services
- Service d'authentification (JWT auth, bcrypt, gestion des utilisateurs)
- Service de produits (CRUD, gestion de stock, émission d'événements produits)
- Service de ventes (création de ventes, décrémentation de stock, émission d'événements de ventes)
- Service de prévision (consommation des événements de ventes, endpoint de prévision ARIMA)
- Service ETL (émission de données synthétiques)

## English

This project is a comprehensive sales forecasting and inventory management application that integrates:
- A backend developed with Flask and PostgreSQL
- A responsive user interface built with React and TypeScript
- A data engineering (ETL) system for data processing
- Machine learning models for sales forecasting

### Services
- Auth service (JWT auth, bcrypt, users)
- Products service (CRUD, stock, emits product events)
- Sales service (sales creation, stock decrement, emits sales events)
- Forecast service (consumes sales events, ARIMA forecast endpoint)
- ETL service (synthetic data emission)

## Quick start

Prereqs: Docker and Docker Compose.

```bash
docker compose up --build
```

Services:
- Auth: http://localhost:8001
- Products: http://localhost:8002
- Sales: http://localhost:8003
- Forecast: http://localhost:8004
- ETL: http://localhost:8010
- Kafka broker: localhost:9092
- PostgreSQL: localhost:5432

Each service exposes `/metrics` for Prometheus and `/health`.

## Environment variables
- `DB_URL` (default: `postgresql+psycopg2://postgres:postgres@postgres:5432/postgres`)
- `DB_SCHEMA` (service-specific, defaults set in compose)
- `JWT_ALGORITHM` (HS256 or RS256)
- `JWT_SECRET` (required if HS256)
- `JWT_PRIVATE_KEY_PATH`, `JWT_PUBLIC_KEY_PATH` (required for RS256)
- `KAFKA_BOOTSTRAP_SERVERS` (default: `kafka:9092`)

## Kafka topics and schemas
- product.created
  - `{ product_id, sku, name, price, stock, ts }`
- product.updated
- product.deleted
- sales.created
  - `{ sale_id, product_id, quantity, price, sold_at, user_id }`

## Endpoints

Auth-service:
- POST `/api/auth/register` { name, email, password, role }
- POST `/api/auth/login` { email, password } -> `{ access_token, refresh_token }`
- POST `/api/auth/refresh` { refresh_token }
- GET `/api/auth/me` (Bearer token)

Products-service (Bearer token required):
- GET `/api/products`
- POST `/api/products` { name, sku, price, stock }
- GET `/api/products/{id}`
- PUT `/api/products/{id}`
- DELETE `/api/products/{id}`

Sales-service (Bearer token required):
- POST `/api/sales` { product_id, quantity, sold_at, price? }
- GET `/api/sales?product_id=&from=&to=&page=&limit=`

Forecast-service:
- GET `/api/forecast?product_id=ID&horizon_days=7`

## Full flow (curl)
```bash
# 1) Register admin
curl -s -X POST http://localhost:8001/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Admin","email":"admin@example.com","password":"admin123","role":"admin"}'

# 2) Login
TOKENS=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"admin123"}')
ACCESS=$(echo $TOKENS | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3) Add product
curl -s -X POST http://localhost:8002/api/products \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"name":"Widget","sku":"WGT-1","price":19.99,"stock":100}'

# 4) Create sale
NOW=$(date -u +%Y-%m-%dT%H:%M:%S)
curl -s -X POST http://localhost:8003/api/sales \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d "{\"product_id\":1,\"quantity\":2,\"sold_at\":\"$NOW\"}"

# 5) Forecast
curl -s "http://localhost:8004/api/forecast?product_id=1&horizon_days=7"
```

## Kafka CLI examples
Open a shell into the Kafka container:
```bash
docker compose exec kafka bash
```
Produce:
```bash
kafka-console-producer --broker-list localhost:9092 --topic sales.created
>{"sale_id":1,"product_id":1,"quantity":1,"price":9.99,"sold_at":"2024-01-01T00:00:00","user_id":1}
```
Consume:
```bash
kafka-console-consumer --bootstrap-server localhost:9092 --topic sales.created --from-beginning
```

## Frontend integration
- Set `VITE_API_URL` in `frontend/.env` to your gateway or directly to auth-service base (e.g., `http://localhost:8001/api`).
- Login form should POST to `/api/auth/login`, then store `access_token` (in memory or localStorage) and use `Authorization: Bearer <token>` for requests to products and sales services.

## CI/CD

Ce projet utilise GitHub Actions pour l'intégration continue (CI) et le déploiement continu (CD).

### Intégration Continue (CI)

Le workflow CI est déclenché à chaque push et pull request. Il effectue les actions suivantes :
- Installation des dépendances du backend
- Exécution des tests du backend
- Construction du conteneur backend
- Installation des dépendances du frontend
- Construction du frontend

### Déploiement Continu (CD)

Le workflow CD est déclenché à chaque push sur les branches main ou master. Il effectue les actions suivantes :
- Connexion à Docker Hub (nécessite la configuration des secrets)
- Construction et publication des images Docker du backend et du frontend
- Déploiement automatique (à configurer selon votre environnement)

Pour activer le CD, ajoutez les secrets suivants dans les paramètres de votre dépôt GitHub :
- `DOCKER_HUB_USERNAME` : votre nom d'utilisateur Docker Hub
- `DOCKER_HUB_TOKEN` : votre token d'accès Docker Hub
- `SSH_HOST` : l'adresse IP ou le nom d'hôte de votre serveur cloud
- `SSH_USERNAME` : le nom d'utilisateur pour la connexion SSH
- `SSH_PRIVATE_KEY` : la clé privée SSH pour l'authentification
- `SSH_PORT` : le port SSH (généralement 22)

## Testing
```bash
pip install -r backend/app/requirements.txt pytest
cd backend && pytest -q
```

## Notes
- DB tables are auto-created on startup for simplicity. For production, add Alembic migrations per service/schema.
- Forecast-service maintains in-memory series and is idempotent by tracking processed `sale_id`s.
- L'application utilise des modèles d'apprentissage automatique (ARIMA) pour la prévision des ventes basée sur les données historiques.
