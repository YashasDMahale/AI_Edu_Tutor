import os
import networkx as nx
from groq import Groq
import json

graph = nx.Graph()

def extract_entities_and_update_graph(text: str):
    groq_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not groq_key or not text.strip():
        return list(graph.nodes)

    client = Groq(api_key=groq_key)
    
    # Limit text to avoid token limits for extraction
    prompt = (
        "Extract key entities and their relationships from the following text. "
        "Return the result as a JSON object with a key 'triplets' containing a list of objects: "
        "{\"triplets\": [{\"subject\": \"...\", \"relation\": \"...\", \"object\": \"...\"}]}. "
        "Keep entities concise. Only return valid JSON.\n\n"
        f"Text: {text[:2000]}"
    )

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=groq_model,
        )
        content = response.choices[0].message.content
        # Basic JSON extraction from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        triplets = data.get("triplets", [])
        
        for t in triplets:
            if isinstance(t, dict) and "subject" in t and "object" in t:
                graph.add_edge(t["subject"], t["object"], relation=t.get("relation", "related_to"))
    except Exception as e:
        print(f"Graph Extraction Error: {e}")
        
    return list(graph.nodes)

def get_graph_context():
    # Return a summary of relationships for LLM context
    context = []
    for u, v, d in list(graph.edges(data=True))[:30]:
        context.append(f"{u} --({d.get('relation')})--> {v}")
    return context
