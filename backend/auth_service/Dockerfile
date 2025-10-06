FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/shared /app/shared
COPY backend/auth_service /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["python", "wsgi.py"]
