# AI Agent PoC

This project is a FastAPI-based application that integrates with the Ollama model (`phi4-mini`) to generate responses and perform Retrieval-Augmented Generation (RAG). It supports both standard and streaming responses.

---

## Features

- **Generate Text**: Generate responses based on a given prompt.
- **RAG (Retrieval-Augmented Generation)**: Generate responses using context retrieved dynamically.
- **Streaming Responses**: Stream responses in chunks for faster perceived response times.

---

## Prerequisites

- **Python 3.12** or higher
- **Docker** (if running with Docker)
- **Ollama CLI** (installed automatically in the Docker image)

---

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd aiagent-poc
```

### 2. Install Dependencies
If running locally without Docker:
```bash
pip install -r requirements.txt
```

---

## Running the Application

### 1. Run Locally
Start the FastAPI application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Run with Docker
Build and run the Docker container:
```bash
docker build -t aiagent-poc .
docker run -p 8000:8000 aiagent-poc
```

---

## Endpoints

### 1. **Generate Text**
- **Endpoint**: `POST /generate`
- **Description**: Generate a response based on a given prompt.
- **Request Body**:
    ```json
    {
        "prompt": "What is the purpose of Phi-4-mini?",
        "max_tokens": 100,
        "temperature": 0.7
    }
    ```
- **Example**:
    ```bash
    curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d '{
        "prompt": "What is the purpose of Phi-4-mini?",
        "max_tokens": 100,
        "temperature": 0.7
    }'
    ```

### 2. **RAG (Retrieval-Augmented Generation)**
- **Endpoint**: `POST /rag`
- **Description**: Generate a response using dynamically retrieved context.
- **Request Body**:
    ```json
    {
        "query": "What are the benefits of Phi-4-mini?",
        "context": "Phi-4-mini is a lightweight open model built upon synthetic data."
    }
    ```
- **Example**:
    ```bash
    curl -X POST "http://localhost:8000/rag" -H "Content-Type: application/json" -d '{
        "query": "What are the benefits of Phi-4-mini?",
        "context": "Phi-4-mini is a lightweight open model built upon synthetic data."
    }'
    ```

### 3. **RAG Streaming**
- **Endpoint**: `GET /rag-stream`
- **Description**: Stream the response for a query using dynamically retrieved context.
- **Query Parameters**:
    - `query`: The user query.
    - `top_k`: The number of top relevant documents to retrieve for context (default: 1).
- **Example**:
    ```bash
    curl "http://localhost:8000/rag-stream?query=What%20are%20the%20benefits%20of%20Phi-4-mini?&top_k=2"
    ```

---

## Notes

- The `ollama` CLI is used to serve the `phi4-mini` model. The Dockerfile ensures the model is pulled and served automatically.
- If running locally, ensure the `ollama` CLI is installed and the `phi4-mini` model is pulled:
    ```bash
    ollama pull phi4-mini
    ollama serve
    ```

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'sentence_transformers'`**:
    Ensure `sentence-transformers` is installed:
    ```bash
    pip install sentence-transformers
    ```

- **Docker Build Issues**:
    Ensure Docker is installed and running. Rebuild the image if necessary:
    ```bash
    docker build --no-cache -t aiagent-poc .
    ```

---

## License

This project is licensed under the MIT License.