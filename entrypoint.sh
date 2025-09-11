#!/bin/sh

# Start the Ollama server in the background
ollama serve &

# Wait for the Ollama server to start
sleep 5

# Pull the required model
ollama pull phi4-mini

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000