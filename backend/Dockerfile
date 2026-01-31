# Use official lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies (needed for some python packages like asyncpg build)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' jarvisuser
USER jarvisuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
