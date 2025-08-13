FROM python:3.11-slim

# Install Node.js 20
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node deps
COPY package.json .
RUN npm install --omit=dev

# App code (keeps your templates/uploads layout intact)
COPY . .

# Render provides $PORT; serve via gunicorn
ENV PYTHONUNBUFFERED=1 FLASK_ENV=production
CMD exec gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 2 app:app
