import requests

from config.settings import Settings


def send_message_telegram(chat_id, text):
    method = "sendMessage"
    token = Settings.token_telegram
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    return requests.post(url, data=data)