import requests

from settings import TOKEN_Telegram


def send_message(chat_id, text):
    method = "sendMessage"
    token = TOKEN_Telegram
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)