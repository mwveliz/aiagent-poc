#!/bin/sh

# Start the Ollama server in the background
ollama serve &

# Wait for the Ollama server to start
sleep 5

# Start the FastAPI application
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers=10