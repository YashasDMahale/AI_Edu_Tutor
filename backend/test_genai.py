from dotenv import load_dotenv
import os
from google import genai
import traceback

load_dotenv()

try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    with open("dummy.txt", "w") as f:
        f.write("hello")
    print("Uploading dummy.txt to Gemini File API...")
    uploaded_file = client.files.upload(file="dummy.txt")
    print(f"Uploaded! {uploaded_file.name}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
