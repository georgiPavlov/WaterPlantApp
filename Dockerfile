# WaterPlantApp Django Container
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    python3-dev \
    python3-pip \
    python3-venv \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Set execute permissions
RUN chmod +x setup.sh start.sh test.sh

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/admin/ || exit 1

# Default command
CMD ["python3", "pycharmtut/manage.py", "runserver", "0.0.0.0:8001"]
