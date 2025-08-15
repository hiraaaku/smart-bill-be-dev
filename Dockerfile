# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies sistem (untuk Pillow)
RUN apt-get update && \
    apt-get install -y libjpeg-dev zlib1g-dev libpng-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy kode
COPY . .

# Expose port
EXPOSE 5000

# Run app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]