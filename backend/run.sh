#!/bin/bash

alembic upgrade head
python3 ./scripts/seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
