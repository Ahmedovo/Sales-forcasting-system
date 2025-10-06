FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/shared /app/shared
COPY backend/etl_service /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8010

CMD ["python", "cli.py"]
