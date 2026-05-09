FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (ffmpeg for youtube processing)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*
    
# Install python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Default command (overridden by docker-compose for development)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
