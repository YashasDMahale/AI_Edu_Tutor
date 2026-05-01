import os
import networkx as nx

graph = nx.Graph()

def extract_entities_and_update_graph(text: str):
    # A simple implementation of knowledge graph node extraction
    # In a real app, this would use an LLM or SpaCy to extract subjects, objects, relations.
    words = text.split()
    # Mocking extraction by picking large words as 'entities'
    entities = list(set([word for word in words if len(word) > 8]))
    
    # Add nodes and edges
    for i in range(len(entities) - 1):
        graph.add_edge(entities[i], entities[i+1])
        
    return list(graph.nodes)

def get_graph_context():
    return list(graph.nodes)[:50]
