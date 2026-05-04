#!/bin/bash

set -e

echo "Running migration..."
uv run alembic upgrade head

echo "Starting fast api..."
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000