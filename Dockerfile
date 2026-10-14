FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy and make startup script executable
COPY render-start.sh /app/render-start.sh
RUN chmod +x /app/render-start.sh

# Create media directory
RUN mkdir -p /app/media

# Expose port
EXPOSE 8000

# Use startup script that handles migrations and seeding
CMD ["/app/render-start.sh"]
