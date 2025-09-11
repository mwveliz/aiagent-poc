# Stage 1: Download the Ollama model
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI
RUN curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama server in the background and pull the model
RUN ollama serve & \
    sleep 5 && \
    ollama pull phi4-mini

# Stage 2: Final image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama CLI
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy the pre-downloaded model from the builder stage
COPY --from=builder /root/.ollama /root/.ollama

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set up the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port used by the FastAPI application
EXPOSE 8000

# Use the entrypoint script to start the server
ENTRYPOINT ["/entrypoint.sh"]