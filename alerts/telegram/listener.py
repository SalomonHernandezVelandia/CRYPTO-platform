from src.api.telegram.client import get_updates

from alerts.telegram.commands.add_command import handle_add_command
from alerts.telegram.commands.sell_command import handle_sell_command
from alerts.telegram.commands.history_command import handle_history_command
from alerts.telegram.commands.portfolio_command import handle_portfolio_command
from alerts.telegram.commands.stats_command import handle_stats_command
from alerts.telegram.commands.request_command import handle_request_command

offset = None



# =============== FUNCION PRINCIPAL ==================================
def check_telegram_updates():
    global offset
    response = get_updates(offset)                              # Telegram devuelve mensajes.
    print(response)

    for result in response["result"]:                           # Procesas uno por uno.
        offset = result["update_id"] + 1                        # Evita duplicados.

        message = (                                             # Extrae mensaje, puede venir mensaje privado, canal o vacio
            result.get("message")
            or result.get("channel_post")
            or {}
        )
        chat_id = message.get("chat", {}).get("id")             # Necesario para responder.
        text = message.get("text", "")                          # Obtener texto, por ejemplo: /add SALOMON BTCUSDT 500
        print(message)

        # =========================
        # ROUTER  COMMAND
        # =========================
        if text.startswith("/add"):
            handle_add_command(chat_id,text)

        elif text.startswith("/sell"):
            handle_sell_command(chat_id,text)

        elif text.startswith("/history"):
            handle_history_command(chat_id,text)

        elif text.startswith("/portfolio"):
            handle_portfolio_command(chat_id,text)

        elif text.startswith("/stats"):
            handle_stats_command(chat_id,text)

        elif text.startswith("/request"):
            handle_request_command(chat_id, text)