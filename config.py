import os
import logging
from dotenv import load_dotenv

# Load environment variables once when the module is imported
load_dotenv()


def load_environment_variables():
    """
    Load and validate essential environment variables for the application.

    Returns:
        tuple[str, str, str]: (alert_type, league_id, user_id)

    Raises:
        ValueError: If required environment variables are missing.
    """
    alert_type = os.getenv("ALERT_TYPE", "weekly").lower()
    league_id = os.getenv("SLEEPER_LEAGUE_ID")
    user_id = os.getenv("SLEEPER_USER_ID")

    if not league_id:
        raise ValueError("Missing required environment variable: SLEEPER_LEAGUE_ID")

    if not user_id:
        logging.warning("SLEEPER_USER_ID not set. Some features may be limited.")

    return alert_type, league_id, user_id
