#!/bin/bash

CLEAN_BUILD=false
RUN_MIGRATIONS=false

# Check for -c flag
while getopts "cm" opt; do
  case $opt in
    c)
      CLEAN_BUILD=true
      ;;
    m)
      RUN_MIGRATIONS=true
      ;;
    *)
      ;;
  esac
done

echo "=== Starting services ==="

if [ "$CLEAN_BUILD" = true ]; then
  echo "Performing clean build..."
  docker compose build --no-cache
  docker compose up --force-recreate
else
  echo "Starting existing containers..."
  docker compose up -d
fi

# Run migrations if requested
if [ "$RUN_MIGRATIONS" = true ]; then
  echo "Running Django migrations..."
  docker exec django_backend python manage.py makemigrations
  docker exec django_backend python manage.py migrate
fi

echo "Frontend: http://localhost:5173"
echo "Backend (API): http://localhost:8000"
echo "LLM: http://localhost:5433"
