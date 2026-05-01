import os
from google import genai

def extract_text_from_media(file_path: str, file_type: str) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=gemini_key)
    
    # Map basic file_type to MIME type for Gemini
    mime_type = "application/octet-stream"
    if file_type == "image":
        # Let the SDK infer or assume jpeg if it's generic 'image'
        # But we upload the file directly so the SDK can infer from extension if present
        prompt = "Extract all readable text from this image accurately. Include all visible text. Do not add any extra commentary."
    elif file_type == "audio":
        prompt = "Provide a highly accurate transcription of this audio. Do not add any extra commentary."
    else:
        raise ValueError(f"Unsupported media type for extraction: {file_type}")

    # Upload the file to Gemini File API
    print(f"Uploading {file_type} to Gemini File API...", flush=True)
    uploaded_file = client.files.upload(file=file_path)
    
    # Wait until the file is ACTIVE (processed)
    import time
    for _ in range(20):
        if str(uploaded_file.state).endswith('ACTIVE'):
            break
        time.sleep(2)
        uploaded_file = client.files.get(name=uploaded_file.name)
    
    try:
        print(f"Generating content for {file_type}...", flush=True)
        response = client.models.generate_content(
            model='models/gemini-2.5-flash',
            contents=[uploaded_file, prompt]
        )
        return response.text
    except Exception as e:
        # Fallback to gemini-2.0-flash if 2.5 is unavailable
        print(f"Failed with gemini-2.5-flash, trying gemini-2.0-flash. Error: {e}", flush=True)
        response = client.models.generate_content(
            model='models/gemini-2.0-flash',
            contents=[uploaded_file, prompt]
        )
        return response.text
    finally:
        # Clean up the file from Gemini's servers
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception:
            pass
