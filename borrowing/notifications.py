import urllib.parse
import urllib.request
from django.conf import settings


def send_telegram_message(message: str) -> None:
    """Надсилає повідомлення у Telegram чат розробника/адміна"""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("Telegram bot token or chat ID is not configured.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        request = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                print(f"Failed to send Telegram message. Status: {response.status}")
    except Exception as e:
        print(f"Error while sending Telegram notification: {e}")
