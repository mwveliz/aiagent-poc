from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from starlette.middleware.cors import CORSMiddleware
from .rag.rag import generate_response_with_rag  # Import RAG logic
from starlette.responses import StreamingResponse
import ollama

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



model_name = "phi4-mini"
model_name = "tinyllama:1.1b"
model_name = "qwen2:7b-instruct-q4_0"

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7

@app.post("/generate")
async def generate_text(request: GenerateRequest):
    response = ollama.generate(
        model=model_name,
        prompt=request.prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    return {"response": response['response']}

class RAGRequest(BaseModel):
    query: str
    context: str

@app.post("/rag")
async def rag_endpoint(request: RAGRequest):
    response = generate_response_with_rag(request.query, request.context, model=model_name)
    return {"response": response}


@app.get("/rag-stream")
async def rag_stream_endpoint(query: str, context: str):
    async def stream():
        prompt = f"Based on the following context, answer the question:\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
        response = ollama.generate(model=model_name, prompt=prompt)  # Generate the full response
        full_response = response['response']
        chunk_size = 50  # Define the size of each chunk
        for i in range(0, len(full_response), chunk_size):
            yield full_response[i:i + chunk_size]  # Yield chunks of the response

    return StreamingResponse(stream(), media_type="text/plain")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
