"""Sends a file to a Telegram chat through the Bot API."""
import requests


def send_document(token: str, chat_id: str, file_path: str, caption: str = "") -> None:
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, "rb") as f:
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": f},
            timeout=60,
        )
    if not resp.ok:
        # Don't print the URL: it contains the bot token.
        raise RuntimeError(f"Telegram error {resp.status_code}: {resp.text}")
