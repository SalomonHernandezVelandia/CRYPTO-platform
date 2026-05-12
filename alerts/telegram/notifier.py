import requests                         # Sirve para hacer: peticiones HTTP, llamadas APIs, requests GET/POST



class TelegramNotifier:

    def __init__(self, token, chat_id):                                     # Se ejecuta cuando se llama: notifier = TelegramNotifier(TOKEN, CHAT_ID)
        self.token = token
        self.chat_id = chat_id                                              # A qué chat enviar mensajes, usuario, grupo, canal
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"       # Esto es el endpoint. sendMessage es basicamente enviar mensaje


    # Método para enviar texto.
    def send_message(self, message):
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",                                       # Le dice a Telegram: interpreta formato Markdown
            "disable_web_page_preview": True                                # Evita que Telegram muestre previews de links.
        }

        try:
            response = requests.post(self.url, data=payload)                # Aquí ocurre realmente el envío.
            if response.status_code != 200:
                print("Error enviando mensaje:", response.text)
            else:
                print("✅Mensaje enviado a Telegram")
        except Exception as e:
            print("Error:", e)


    # Método para enviar imágenes.
    def send_photo(self, photo_path, caption=""):
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"         # Telegram tiene endpoints separados.

        with open(photo_path, "rb") as photo:
            files = {"photo": photo}
            data = {
                "chat_id": self.chat_id,
                "caption": caption,                                         # Texto debajo de la imagen.
                "parse_mode": "Markdown"
            }

            response = requests.post(url, files=files, data=data)
            if response.status_code != 200:
                print("Error enviando imagen:", response.text)
            else:
                print("✅Imagen enviada a Telegram")