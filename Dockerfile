# apps/bus-fleet-manager/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true
RUN pip install gunicorn

COPY . .

# Flask typically runs on 5000 inside the container
EXPOSE 5000

# Use Gunicorn for production, binding to 0.0.0.0
# Render sets the PORT env var, but gunicorn needs explicit bind
# We use a shell command to interpret the PORT variable properly
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
