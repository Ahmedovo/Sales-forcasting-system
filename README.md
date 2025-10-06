# Microservices Backend (Flask, PostgreSQL, Kafka)

Services:
- auth-service (JWT auth, bcrypt, users)
- products-service (CRUD, stock, emits product events)
- sales-service (sales creation, stock decrement, emits sales events)
- forecast-service (consumes sales events, ARIMA forecast endpoint)
- etl-service (synthetic data emission over Kafka)

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

## Testing
```bash
pip install -r backend/auth_service/requirements.txt pytest
cd backend/auth_service && pytest -q
```

## Notes
- DB tables are auto-created on startup for simplicity. For production, add Alembic migrations per service/schema.
- Forecast-service maintains in-memory series and is idempotent by tracking processed `sale_id`s.
