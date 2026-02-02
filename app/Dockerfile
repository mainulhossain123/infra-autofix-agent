FROM python:3.14-slim

WORKDIR /usr/src/app

# Install build dependencies for ARM64 compatibility
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5000

# Run the application
CMD ["python", "app.py"]
