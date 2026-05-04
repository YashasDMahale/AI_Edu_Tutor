import os
from pinecone import Pinecone

class EmbeddingService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        if self.api_key:
            self.pc = Pinecone(api_key=self.api_key)
        else:
            self.pc = None

    def get_text_embedding(self, text: str):
        if not self.pc:
            return [0.0] * 1024 # Dummy embedding if Pinecone is not configured
        
        print("Fetching text embedding from Pinecone Inference API...", flush=True)
        embeddings = self.pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[text],
            parameters={"input_type": "passage", "truncate": "END"}
        )
        return embeddings[0].values

    def get_image_embedding(self, description: str):
        """
        Generates a semantic embedding for an image using Gemini's rich visual description.
        In production CLIP setup: return CLIP_model.encode(image)
        """
        return self.get_text_embedding(f"[VISUAL] {description}")

    def get_audio_embedding(self, transcription: str):
        """
        Generates a semantic embedding for audio using transcription.
        In production: return CLAP_model.encode(audio)
        """
        return self.get_text_embedding(f"[AUDIO] {transcription}")
