import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def format_alert_message(alert: dict) -> str:
    if "ownership" in alert:
        return (
            f"⚠️ Player *{alert['player_id']}*\n"
            f"Ownership: {alert['ownership']:.1f}%\n"
            f"Transaction: {alert['type']}\n"
            f"Week: {alert['week']}"
        )
    else:
        return (
            f"⚡ Player {alert['player_id']} | TD: {alert['td']} | "
            f"Fumble: {alert['fumble']} | Interception: {alert['interception']}"
        )


def send_message(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials not set")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Telegram message failed: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


def send_alerts(alerts: list):
    if not alerts:
        print("No alerts to send.")
        return
    for alert in alerts:
        # message = format_alert_message(alert)
        message = alert["message"]
        send_message(message)
