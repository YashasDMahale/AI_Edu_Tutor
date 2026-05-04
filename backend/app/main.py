from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

from .services.db_service import PineconeService
from .services.embedding_service import EmbeddingService
from .services.media_service import extract_text_from_media
from .services.graph_service import extract_entities_and_update_graph
from .services.llm_service import generate_response

import fitz  # PyMuPDF

app = FastAPI(title="Multi-Modal Smart Education Tutor", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
pinecone_service = PineconeService()
embedding_service = EmbeddingService()

UPLOAD_DIR = "/app/temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.delete("/clear")
async def clear_database():
    try:
        pinecone_service.clear()
        return {"message": "Database cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), file_type: str = Form(...)):
    if file_type not in ["pdf", "image", "audio"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Must be pdf, image, or audio.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    extracted_text = ""
    embedding = None
    chunks = []
    
    try:
        if file_type == "pdf":
            with fitz.open(file_path) as doc:
                for page in doc:
                    extracted_text += page.get_text()
            # Simple chunking
            chunk_size = 1000
            chunks = [extracted_text[i:i+chunk_size] for i in range(0, len(extracted_text), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                emb = embedding_service.get_text_embedding(chunk)
                pinecone_service.upsert(
                    f"{file.filename}-chunk-{i}",
                    emb,
                    {"source_type": "pdf", "file_name": file.filename, "text": chunk}
                )
            
            extract_entities_and_update_graph(extracted_text)
            
        elif file_type in ["image", "audio"]:
            extracted_text = extract_text_from_media(file_path, file_type)
            if not extracted_text:
                extracted_text = ""
            
            # Larger chunking for media text to keep transcriptions together
            chunk_size = 5000
            chunks = [extracted_text[i:i+chunk_size] for i in range(0, len(extracted_text), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                if file_type == "image":
                    emb = embedding_service.get_image_embedding(chunk)
                else: # audio
                    emb = embedding_service.get_audio_embedding(chunk)
                    
                pinecone_service.upsert(
                    f"{file.filename}-chunk-{i}",
                    emb,
                    {"source_type": file_type, "file_name": file.filename, "text": chunk}
                )
            
            extract_entities_and_update_graph(extracted_text)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        return {"message": "File processed successfully", "file_name": file.filename, "modality": file_type}

    except Exception as e:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_system(req: QueryRequest):
    question = req.question
    question_embedding = embedding_service.get_text_embedding(question)
    
    # Retrieve top K
    matches = pinecone_service.query(question_embedding, top_k=3)
    
    context = ""
    sources = []
    for match in matches:
        metadata = match.get('metadata', {})
        text = metadata.get('text', '')
        file_name = metadata.get('file_name', 'Unknown File')
        source_type = metadata.get('source_type', 'unknown')
        context += f"SOURCE: {file_name} ({source_type})\nCONTENT: {text}\n---\n"
        sources.append({
            "source_type": metadata.get('source_type'),
            "file_name": metadata.get('file_name'),
            "score": match.get('score')
        })
        
    answer = generate_response(question, context)
    return {
        "answer": answer,
        "sources": sources
    }
