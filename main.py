import os
from dotenv import load_dotenv
from league_tools import League, get_last_week_number, get_max_weeks_by_month
from alerts import weekly_alerts, daily_alerts, live_game_alerts
from telegram_bot import send_alerts

load_dotenv()

ALERT_TYPE = os.environ.get("ALERT_TYPE", "weekly")
LEAGUE_ID = os.environ.get("SLEEPER_LEAGUE_ID")
USER_ID = os.environ.get("SLEEPER_USER_ID")

league = League(LEAGUE_ID)
max_weeks = get_max_weeks_by_month()
last_week = get_last_week_number(league, max_weeks)

alerts: list = []

if ALERT_TYPE == "weekly":
    alerts = weekly_alerts(league, last_week)
elif ALERT_TYPE == "daily":
    alerts = daily_alerts(league, last_week)
elif ALERT_TYPE == "live":
    alerts = []
#     live_game_alerts(league, USER_ID)

send_alerts(alerts)
