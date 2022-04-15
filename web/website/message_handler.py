from flask_login import current_user
import requests

TG_TOKEN = '5271671736:AAFezCr4E-g3m2QrQQh6U8FA4_nUJB5zKuo'

def on_recieve(message):
    chatId = message["message"]["chat"]["id"]
    text = message["message"]["text"]

    if(text.split()[0].lower() == 'привязать'):
        return 'connect'

    return 0

def send_message(chat_id, text):
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{TG_TOKEN}/{method}"
    data = {"chat_id": chat_id, "text": text}
    return requests.post(url, data=data)