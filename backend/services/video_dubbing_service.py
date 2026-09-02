"""ElevenLabs video/audio dubbing integration.

The API key stays on the server. This service uses the currently documented
Dubbing API to create asynchronous dubbing jobs and retrieve the finished
MP3/MP4 output through the backend.
"""
import os
from pathlib import Path
import requests

API_URL = "https://api.elevenlabs.io/v1/dubbing"


def _key():
    return os.getenv("ELEVENLABS_API_KEY", "").strip()


def configured():
    return bool(_key())


def _headers():
    return {"xi-api-key": _key()}


def create_dub(*, file_storage=None, source_url=None, source_lang=None,
               target_lang=None, name="Bhasha Shiksha Setu"):
    if not configured():
        raise RuntimeError("Video dubbing is not configured. Add ELEVENLABS_API_KEY in Render environment variables.")
    if not target_lang:
        raise ValueError("Target language is required.")
    if not file_storage and not source_url:
        raise ValueError("Upload a video or provide a public video URL.")

    data = {
        "name": name[:200],
        "target_lang": target_lang,
        "source_lang": source_lang or "auto",
        "num_speakers": "0",
        "watermark": "false",
        "highest_resolution": "true",
    }
    files = None
    if file_storage:
        file_storage.stream.seek(0)
        files = {"file": (
            file_storage.filename or "video.mp4",
            file_storage.stream,
            file_storage.mimetype or "application/octet-stream",
        )}
    else:
        data["source_url"] = source_url.strip()

    r = requests.post(API_URL, headers=_headers(), data=data, files=files, timeout=90)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text[:500]
        raise RuntimeError(f"Dubbing provider error ({r.status_code}): {detail}")
    return r.json()


def get_dub(dubbing_id):
    if not configured():
        raise RuntimeError("Video dubbing is not configured.")
    r = requests.get(f"{API_URL}/{dubbing_id}", headers=_headers(), timeout=30)
    if not r.ok:
        raise RuntimeError(f"Could not read dubbing status ({r.status_code}).")
    return r.json()


def download_dub(dubbing_id, language_code):
    if not configured():
        raise RuntimeError("Video dubbing is not configured.")
    r = requests.get(
        f"{API_URL}/{dubbing_id}/audio/{language_code}",
        headers=_headers(), timeout=120, stream=True,
    )
    if not r.ok:
        raise RuntimeError(f"Could not download dubbed media ({r.status_code}).")
    return r


def delete_dub(dubbing_id):
    if not configured():
        raise RuntimeError("Video dubbing is not configured.")
    r = requests.delete(f"{API_URL}/{dubbing_id}", headers=_headers(), timeout=30)
    if not r.ok:
        raise RuntimeError(f"Could not delete dubbing ({r.status_code}).")
    return r.json()
