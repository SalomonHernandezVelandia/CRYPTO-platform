import requests
import os

from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

SEND_URL = f"{BASE_URL}/sendMessage"                # endpoint para enviar mensaje
GET_URL = f"{BASE_URL}/getUpdates"
IMG_URL = f"{BASE_URL}/sendPhoto"

DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")





def send_message(chat_id=None, text=""):
    if chat_id is None:
        chat_id = DEFAULT_CHAT_ID

    payload = {                                     # Para que telegram sepa a quien enviar y que enviar
        "chat_id": chat_id,
        "text": text
    }

    return requests.post(SEND_URL, json=payload)    # Hace el envío.




def get_updates(offset=None):
    params = {}
    if offset:
        params["offset"] = offset

    response = requests.get(GET_URL, params=params)

    return response.json()



# Método para enviar imágenes.
def send_photo(chat_id=None, photo_path="", caption=""):
    if chat_id is None:
        chat_id = DEFAULT_CHAT_ID
        
    with open(photo_path, "rb") as photo:
        files = {"photo": photo}

        data = {
            "chat_id": chat_id,
            "caption": caption,                             # Texto debajo de la imagen.
            "parse_mode": "Markdown"
        }

        return requests.post(IMG_URL, files=files, data=data)
    