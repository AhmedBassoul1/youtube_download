FROM python:3.11-slim

WORKDIR /app

# Copy the frontend files
COPY . .

# Run the simple server
CMD ["python3", "-m", "http.server", "8080"]
