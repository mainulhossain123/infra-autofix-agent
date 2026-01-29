FROM python:3.11-slim

WORKDIR /usr/src/bot

# Install build dependencies for ARM64 compatibility
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Expose metrics port
EXPOSE 8000

# Run both the bot and metrics server
CMD python metrics_server.py & python bot.py
