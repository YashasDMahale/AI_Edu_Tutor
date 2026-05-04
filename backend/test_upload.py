import httpx
import asyncio

async def test_uploads():
    async with httpx.AsyncClient() as client:
        # Create a dummy image (1x1 pixel transparent GIF)
        gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        
        # Create a dummy audio (WAV file with 1 sample)
        wav_bytes = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x04\x00\x00\x00\x00\x00\x00\x00'

        print("Testing image upload...")
        response = await client.post('http://localhost:8000/upload', data={'file_type': 'image'}, files={'file': ('dummy.gif', gif_bytes, 'image/gif')}, timeout=60.0)
        print("Image response:", response.status_code, response.text)

        print("Testing audio upload...")
        response = await client.post('http://localhost:8000/upload', data={'file_type': 'audio'}, files={'file': ('dummy.wav', wav_bytes, 'audio/wav')}, timeout=60.0)
        print("Audio response:", response.status_code, response.text)

asyncio.run(test_uploads())
