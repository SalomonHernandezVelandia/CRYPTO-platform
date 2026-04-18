import requests

class TelegramNotifier:

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"

    def send_message(self, message):

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        try:
            response = requests.post(self.url, data=payload)

            if response.status_code != 200:
                print("❌ Error enviando mensaje:", response.text)
            else:
                print("✅ Mensaje enviado a Telegram")

        except Exception as e:
            print("❌ Error:", e)


    def send_photo(self, photo_path, caption=""):

        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"

        with open(photo_path, "rb") as photo:
            files = {"photo": photo}
            data = {
                "chat_id": self.chat_id,
                "caption": caption,
                "parse_mode": "Markdown"
            }

            response = requests.post(url, files=files, data=data)

            if response.status_code != 200:
                print("❌ Error enviando imagen:", response.text)
            else:
                print("📸 Imagen enviada a Telegram")