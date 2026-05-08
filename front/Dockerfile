FROM python:3.11-slim

WORKDIR /app

# Copy the front folder content
COPY . .

# Command to run the simple http server
CMD ["python3", "-m", "http.server", "8080"]
