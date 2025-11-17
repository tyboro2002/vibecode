FROM python:3.12-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y     gcc     libdbus-1-dev     libdbus-glib-1-dev     build-essential     python3-dev     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--graceful-timout=900", "--timeout=900"]
