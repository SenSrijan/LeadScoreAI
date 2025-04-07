# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV NLTK_DATA=/app/nltk_data

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set NLTK data path
ENV NLTK_DATA=/app/nltk_data

# Create the nltk_data directory and download vader_lexicon there
RUN mkdir -p /app/nltk_data && \
    python -c "import nltk; nltk.download('vader_lexicon', download_dir='/app/nltk_data')"

# Copy full app code
COPY . .

# Expose app port
EXPOSE 8000

# Start with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app:app"]
