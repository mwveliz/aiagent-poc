from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import ollama
import os
from pathlib import Path

# NEW: Import chromadb
import chromadb
from chromadb.utils import embedding_functions

# --- Configuration ---
app = FastAPI()
DOCUMENTS_DIR = Path("my_documents")
CHROMA_PATH = Path("chroma_data") # Directory to store ChromaDB data
DOCUMENTS_DIR.mkdir(exist_ok=True)
CHROMA_PATH.mkdir(exist_ok=True)

# Choose the model for generating the final answer
llm_model_name = "tinyllama:1.1b" 
#llm_model_name = "qwen2:7b-instruct-q4_0"

# This tells Chroma how to turn text into embeddings.
# It will automatically download and use the 'all-MiniLM-L6-v2' model.
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)

# This client persists data to the 'chroma_data' directory.
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

# The collection is where we'll store the documents, embeddings, and metadata.
# We pass the embedding function directly to the collection.
collection = chroma_client.get_or_create_collection(
    name="my_documents_collection",
    embedding_function=sentence_transformer_ef
)

# --- Data Loading and Indexing (Done at Startup) ---
def load_and_index_documents():
    """
    Loads .txt files, chunks them, and adds them to the ChromaDB collection.
    This is now idempotent; it won't re-add existing documents.
    """
    print(f"Loading and indexing documents from '{DOCUMENTS_DIR}'...")
    indexed_files = {metadata['source'] for metadata in collection.get(include=["metadatas"])['metadatas']}
    for filepath in DOCUMENTS_DIR.glob("*.txt"):
        print(f"Buscando en {filepath}")
        if str(filepath) in indexed_files:
            print(f"Skipping '{filepath}', already indexed.")
            continue         
        print(f"Indexing '{filepath}'...")
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            # Simple chunking: split the document by paragraphs
            chunks = text.split('\n\n')
            
            # Create documents, metadatas, and IDs for ChromaDB
            documents_to_add = []
            metadatas_to_add = []
            ids_to_add = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip(): # Avoid empty chunks
                    documents_to_add.append(chunk)
                    metadatas_to_add.append({'source': str(filepath)})
                    # Create a unique ID for each chunk
                    ids_to_add.append(f"{filepath}-{i}")

            if documents_to_add:
                collection.add(
                    documents=documents_to_add,
                    metadatas=metadatas_to_add,
                    ids=ids_to_add
                )

    doc_count = collection.count()
    if doc_count == 0:
        print("⚠️ Warning: No .txt files found or indexed. The RAG context will be empty.")
    else:
        print(f"✅ Collection now contains {doc_count} text chunks.")

# Load documents when the application starts
load_and_index_documents()

# --- Pydantic Models ---
class RAGRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

# --- API Endpoints ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/rag-stream")
async def rag_stream_endpoint(request: RAGRequest):
    async def stream():
        # 1. Retrieve context from ChromaDB
        # The query method automatically handles embedding the query and finding similar documents.
        results = collection.query(
            query_texts=[request.query],
            n_results=request.top_k
        )
        retrieved_chunks = results['documents'][0]
        retrieved_context = "\n\n---\n\n".join(retrieved_chunks)
        # 2. Create the prompt for the language model
        prompt = f"""Based on the following context, answer the question. 
        If the context does not contain the answer, say so.\n\n 
        Context: {retrieved_context}\n\n
        Question: {request.query}\n\nAnswer:"""
        # 3. Stream the response from Ollama
        response_generator = ollama.generate(
            model=llm_model_name, 
            prompt=prompt, 
            stream=True
        )
        for chunk in response_generator:
            if 'response' in chunk:
                yield chunk['response']
    return StreamingResponse(stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
