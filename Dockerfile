# Dockerfile for Yantrik Discord Bot

FROM python:3.12-slim

# Environment settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash botuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies (better caching)
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set permissions
RUN chown -R botuser:botuser /app
USER botuser

# Graceful shutdown for blue/green switching
STOPSIGNAL SIGTERM

# Optional healthcheck (based on process running)
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD pgrep -f base_app.py || exit 1

# Start bot
ENTRYPOINT ["python", "base_app.py"]