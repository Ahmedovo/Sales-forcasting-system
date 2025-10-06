FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/shared /app/shared
COPY backend/forecast_service /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8004

CMD ["python", "wsgi.py"]
