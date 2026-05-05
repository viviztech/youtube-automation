import os
import httpx


async def generate_voiceover(
    text: str,
    voice_id: str,
    api_key: str,
    output_path: str,
) -> dict:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                return {"status": "failed", "error": f"ElevenLabs error {response.status_code}: {response.text}"}

            with open(output_path, "wb") as f:
                f.write(response.content)

        file_size = os.path.getsize(output_path)
        # Estimate duration: ~128kbps MP3 = 16000 bytes/sec
        estimated_duration = round(file_size / 16000, 1)

        return {"status": "done", "path": output_path, "duration_seconds": estimated_duration}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


async def list_voices(api_key: str) -> list[dict]:
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return [{"voice_id": v["voice_id"], "name": v["name"]} for v in data.get("voices", [])]
    except Exception:
        pass
    return [{"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel (default)"}]
