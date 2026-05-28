#!/bin/sh

set -e

echo "Applying scheduler database migrations..."
alembic -c alembic.ini upgrade head

echo "Migrations applied. Executing command: $@"
exec "$@"
