import os
from pinecone import Pinecone, ServerlessSpec

class PineconeService:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "edu-tutor")
        
        if not api_key:
            print("WARNING: PINECONE_API_KEY not set. Pinecone operations will fail.")
            self.index = None
            return

        self.pc = Pinecone(api_key=api_key)
        
        # Check if index exists, else create it
        # Note: assuming 1024 dimension for text embeddings from multilingual-e5-large
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1024,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            
        self.index = self.pc.Index(self.index_name)

    def upsert(self, id: str, embedding: list, metadata: dict):
        if not self.index:
            return
        
        # multilingual-e5-large outputs 1024 dimensions.
        if len(embedding) > 1024:
            embedding = embedding[:1024]
        elif len(embedding) < 1024:
            embedding = embedding + [0.0] * (1024 - len(embedding))

        self.index.upsert(vectors=[(id, embedding, metadata)])

    def query(self, vector: list, top_k: int = 3):
        if not self.index:
            return []
            
        if len(vector) > 1024:
            vector = vector[:1024]
        elif len(vector) < 1024:
            vector = vector + [0.0] * (1024 - len(vector))
            
        result = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return result['matches']

    def clear(self):
        if not self.index:
            return
        # Delete all vectors in the index
        self.index.delete(delete_all=True)
