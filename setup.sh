#!/bin/bash
set -e

echo "=== Setting up project ==="

# Create backend Django project
echo "--- Creating Django project ---"
if [ -e backend ] && [ ! -d backend ]; then
  echo "Error: 'backend' exists and is not a directory."
  read -p "Do you want to remove this file so the directory can be created? (y/n): " choice
  if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    rm backend
    echo "Removed the file 'backend'."
  else
    echo "Aborting setup."
    exit 1
  fi
fi

if [ -d backend ]; then
  echo "WARNING: backend/ directory already exists."
  read -p "Do you want to delete it and start fresh? (y/n): " choice
  if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    rm -rf backend
    echo "Deleted backend/ directory."
  else
    echo "Aborting setup."
    exit 1
  fi
fi

mkdir -p backend
cd backend

# create venv inside backend
python3 -m venv venv
source venv/bin/activate

# Install only needed packages inside venv
pip install django gunicorn psycopg2-binary

# Start Django project
python -m django startproject project .

# freeze *inside venv* to clean requirements.txt
pip freeze > requirements.txt

deactivate
echo "Django project created."

# Create basic Dockerfile for backend
cat <<EOF > Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    gcc \
    libdbus-1-dev \
    libdbus-glib-1-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
EOF

cd ..

# Create frontend Vue project
echo "--- Creating Vue project ---"
if [ ! -d frontend ]; then
    echo "--- Making new frontend folder ---"
    npx create-vite@latest frontend --template vue-ts
    cd frontend
    npm install
else
    echo "--- Frontend already exists, running npm install ---"
    cd frontend
    npm install
fi

# Create basic Dockerfile for frontend
cat <<EOF > Dockerfile
FROM node:20

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install
# COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
EOF

cd ..

# Create docker-compose.yml
echo "--- Creating docker-compose.yml ---"

cat <<EOF > docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: django_backend
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    container_name: vue_frontend
    volumes:
      - ./frontend:/app
      -  frontend_modules:/app/node_modules
    ports:
      - "5173:5173"

  db:
    image: postgres:14
    container_name: postgres_db
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_DB: mydatabase
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
  frontend_modules:
EOF

# Create .env file
echo "--- Creating .env file ---"

cat <<EOF > .env
DJANGO_SECRET_KEY=$(openssl rand -hex 32)
DJANGO_DEBUG=True
EOF

echo "=== Setup complete! ==="
echo "You can now run './start.sh' to start the project."
