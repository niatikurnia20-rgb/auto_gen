import base64
import os

import requests

from config import LMNT_API_KEY, LMNT_LANGUAGE, LMNT_VOICE

LMNT_BASE_URL = "https://api.lmnt.com/v1/ai"
LMNT_TIMEOUT = 60


def _cleanup_partial_file(output_path):
    if os.path.exists(output_path):
        os.remove(output_path)


def _resolve_lmnt_voice():
    if not LMNT_API_KEY:
        raise RuntimeError("LMNT_API_KEY is missing in .env.")

    if LMNT_VOICE:
        return LMNT_VOICE

    response = requests.get(
        f"{LMNT_BASE_URL}/voice/list",
        headers={"X-API-Key": LMNT_API_KEY},
        params={"owner": "all"},
        timeout=LMNT_TIMEOUT,
    )
    response.raise_for_status()

    voices = response.json()
    ready_voices = [voice for voice in voices if voice.get("state") == "ready"]
    if not ready_voices:
        raise RuntimeError("LMNT did not return any ready voices for this account.")

    for predicate in (
        lambda voice: voice.get("starred"),
        lambda voice: voice.get("owner") == "system",
        lambda voice: True,
    ):
        for voice in ready_voices:
            if predicate(voice):
                return voice["id"]

    raise RuntimeError("LMNT voice selection failed.")


def generate_audio(text, output_path):
    if not text or not text.strip():
        raise ValueError("Cannot synthesize empty text.")

    try:
        voice_id = _resolve_lmnt_voice()
        response = requests.post(
            f"{LMNT_BASE_URL}/speech",
            headers={
                "X-API-Key": LMNT_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "voice": voice_id,
                "text": text.strip(),
                "language": LMNT_LANGUAGE,
                "format": "mp3",
            },
            timeout=LMNT_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        audio_base64 = data.get("audio")
        if not audio_base64:
            raise RuntimeError("LMNT response did not contain audio data.")

        audio_bytes = base64.b64decode(audio_base64, validate=True)
        with open(output_path, "wb") as audio_file:
            audio_file.write(audio_bytes)
        return output_path
    except requests.Timeout as e:
        _cleanup_partial_file(output_path)
        raise RuntimeError("LMNT TTS request timed out.") from e
    except requests.HTTPError as e:
        _cleanup_partial_file(output_path)
        detail = ""
        if e.response is not None and e.response.text:
            detail = f" {e.response.text[:300]}"
        raise RuntimeError(
            f"LMNT TTS request failed with status {e.response.status_code}.{detail}".strip()
        ) from e
    except requests.RequestException as e:
        _cleanup_partial_file(output_path)
        raise RuntimeError(f"LMNT TTS connection failed: {e}") from e
    except (ValueError, base64.binascii.Error) as e:
        _cleanup_partial_file(output_path)
        raise RuntimeError(f"LMNT TTS returned invalid audio data: {e}") from e
