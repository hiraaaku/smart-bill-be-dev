# Dockerfile
FROM python:3.11-slim

# Non-interactive mode (untuk apt)
ENV DEBIAN_FRONTEND=noninteractive

# Workdir
WORKDIR /app

# Install system dependencies untuk Pillow & image processing
# libjpeg-dev, zlib1g-dev, libpng-dev, libfreetype6-dev → semua didukung
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libfreetype6-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt dulu (untuk caching)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy kode setelah install dependencies
COPY . .

# Expose port
EXPOSE 5000

# Health check (opsional, tapi bagus untuk production)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run dengan gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--worker-class", "sync", "app:app"]