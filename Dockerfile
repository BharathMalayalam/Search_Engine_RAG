# Multi-stage build: Stage 1 - Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2 - Runtime environment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY app.py .
COPY orchestrator.py .
COPY agents/ ./agents/
COPY data/ ./data/
COPY templates/ ./templates/
COPY checkpoints/ ./checkpoints/
COPY tuned_model_v1/ ./tuned_model_v1/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create a .env file placeholder (users should override at runtime)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Run the Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
