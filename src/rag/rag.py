import ollama

def generate_response_with_rag(query: str, context: str, model: str = "phi4-mini"):
    prompt = f"Based on the following context, answer the question:\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
    response = ollama.generate(model=model, prompt=prompt)
    return response['response']