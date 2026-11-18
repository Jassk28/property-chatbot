# Dockerfile - packages the chatbot into a container
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py data.json ./
COPY templates ./templates

EXPOSE 7860
# Uses the PORT given by the hosting service (Render), or 7860 by default
CMD gunicorn --bind 0.0.0.0:${PORT:-7860} --timeout 120 app:app
