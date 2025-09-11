import ollama

def generate_response_with_rag(query: str, context: str, model: str = "qwen2:7b-instruct-q4_0"):
    prompt = f"Based on the following context, answer the question:\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
    response = ollama.generate(model=model, prompt=prompt)
    return response['response']