FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py send_notification.py ./
COPY data ./data
COPY templates ./templates
COPY static ./static

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# FLASK_SECRET_KEY, GEMINI_API_KEY, EMAIL_USER and EMAIL_PASS are supplied at
# run time (docker run -e ...), never baked into the image.
# FLASK_ENV=production marks the session cookie as HTTPS-only, so put the
# container behind HTTPS or override FLASK_ENV when testing over plain HTTP.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} app:app"]
