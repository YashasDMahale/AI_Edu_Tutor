import os
from groq import Groq

from .graph_service import get_graph_context

def generate_response(question: str, context: str) -> str:
    groq_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not groq_key:
        return "Error: GROQ_API_KEY is not set."

    client = Groq(api_key=groq_key)
    
    graph_context = get_graph_context()
    
    system_prompt = (
        "You are a helpful Multi-Modal Smart Education Tutor. "
        "Use the provided Document Context to answer the user's question. "
        f"Additional Knowledge Graph Concepts: {', '.join(graph_context)}\n"
        "If you cannot answer the question based on the context, say that you don't know."
    )
    
    user_prompt = f"Document Context:\n{context}\n\nQuestion:\n{question}"

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model=groq_model,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with Groq: {str(e)}"
