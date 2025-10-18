import logging
from config import load_environment_variables
from league_tools import League, get_last_week_number, get_max_weeks_by_month
from alerts import weekly_alerts, daily_alerts, live_game_alerts
from telegram_bot import send_alerts


# ✅ Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def build_alerts(alert_type: str, league: League, user_id: str) -> list:
    """
    Build and return the list of alerts depending on the alert type.
    """
    max_weeks = get_max_weeks_by_month()
    last_week = get_last_week_number(league, max_weeks)

    logging.info(f"Building alerts for type '{alert_type}' (Last week: {last_week})")

    if alert_type == "weekly":
        return weekly_alerts(league, last_week)
    elif alert_type == "daily":
        return daily_alerts(league, last_week)
    elif alert_type == "live":
        # Future implementation for live game alerts
        # return live_game_alerts(league, user_id)
        logging.warning("Live game alerts not yet implemented.")
        return []
    else:
        raise ValueError(f"Unknown ALERT_TYPE: {alert_type}")


def main():
    """
    Main entry point for the automated alert handler.
    """
    try:
        alert_type, league_id, user_id = load_environment_variables()
        league = League(league_id)

        alerts = build_alerts(alert_type, league, user_id)

        if alerts:
            send_alerts(alerts)
            logging.info(f"{len(alerts)} alerts sent successfully.")
        else:
            logging.info(f"No alerts generated for type '{alert_type}'.")

    except Exception as e:
        logging.error(f"Error while running alert handler: {e}", exc_info=True)


if __name__ == "__main__":
    main()
