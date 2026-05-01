import os
from google import genai

from .graph_service import get_graph_context

def generate_response(question: str, context: str) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return "Error: GEMINI_API_KEY is not set."

    client = genai.Client(api_key=gemini_key)
    
    graph_context = get_graph_context()
    
    system_prompt = (
        "You are a helpful Multi-Modal Smart Education Tutor. "
        "Use the provided Document Context to answer the user's question. "
        f"Additional Knowledge Graph Concepts: {', '.join(graph_context)}\n"
        "If you cannot answer the question based on the context, say that you don't know."
    )
    
    user_prompt = f"System Instruction: {system_prompt}\n\nDocument Context:\n{context}\n\nQuestion:\n{question}"

    try:
        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=user_prompt
        )
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini: {str(e)}"
