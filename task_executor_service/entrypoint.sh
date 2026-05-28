#!/bin/sh

set -e

echo "Applying executor database migrations..."
alembic -c alembic.ini upgrade head
echo "Starting executor web server..."

exec uvicorn main:app --host 0.0.0.0 --port 8001
