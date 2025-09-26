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
model_name = "llama3:8b-instruct-q6_K"
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

@app.post("/rag-stream")
async def rag_stream_endpoint(request: RAGRequest):
    async def stream():
        # Get query and context from the request body model
        query = request.query
        context = request.context
        
        prompt = f"Based on the following context, answer the question:\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
        
        # Call the synchronous ollama.generate with stream=True
        # This is the correct streaming logic for the ollama library
        response_generator = ollama.generate(
            model=model_name, 
            prompt=prompt, 
            stream=True
        )
        
        # Iterate through the generator and yield the response part
        for chunk in response_generator:
            if 'response' in chunk:
                # yield the text part of the response
                yield chunk['response']
    
    # Return the StreamingResponse with the generator
    return StreamingResponse(stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
