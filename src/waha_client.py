import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://waha:3000").rstrip("/")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")

def _get_headers():
    headers = {"Content-Type": "application/json"}
    if WAHA_API_KEY:
        headers["X-Api-Key"] = WAHA_API_KEY
    return headers

def send_message(chat_id: str, text: str, session: str | None = None) -> dict:
    url = f"{WAHA_BASE_URL}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": session or WAHA_SESSION,
    }
    resp = requests.post(url, json=payload, headers=_get_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json() if resp.content else {"ok": True}

def send_file(chat_id: str, file_path: str, caption: str = "", mimetype: str = "application/octet-stream", session: str | None = None) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    url = f"{WAHA_BASE_URL}/api/sendFile"
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "chatId": chat_id,
        "caption": caption,
        "file": {
            "mimetype": mimetype,
            "filename": os.path.basename(file_path),
            "data": encoded,
        },
        "session": session or WAHA_SESSION,
    }

    resp = requests.post(url, json=payload, headers=_get_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json() if resp.content else {"ok": True}
