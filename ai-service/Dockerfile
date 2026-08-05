FROM python:3.13-slim

WORKDIR /app

# Install system dependencies if required for Qdrant/FastEmbed/BGE Reranker
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create a non-root user for security compliance
RUN useradd -m docent
RUN chown -R docent:docent /app
USER docent

EXPOSE 8000

# Run FastAPI in production mode
CMD ["fastapi", "run", "main.py", "--port", "8000"]
