# Pharmacy Assistant Backend
# FastAPI + SQLite + OpenAI integration

FROM python:3.11-slim

# Set working directory
WORKDIR /app/backend

# Prevent Python from writing bytecode and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run the application
# The database will be created at /app/backend/pharmacy.db
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

