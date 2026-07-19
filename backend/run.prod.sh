#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Running seed script..."
python3 ./scripts/seed.py

echo "Starting Uvicorn (production)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
