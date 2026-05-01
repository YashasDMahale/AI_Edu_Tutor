from sentence_transformers import SentenceTransformer
from faster_whisper import WhisperModel

print("Downloading SentenceTransformers model...")
SentenceTransformer('all-MiniLM-L6-v2')
SentenceTransformer('clip-ViT-B-32')

print("Downloading Whisper model...")
WhisperModel("tiny", device="cpu", compute_type="int8")

print("Models downloaded successfully!")
