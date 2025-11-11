from datetime import datetime
from typing import List, Dict, Any
import pytz

from telegram_bot import send_alerts
from league_tools import fetch_all_transactions, display_standings, League, get_scoreboards_json, get_weekly_drops, \
    get_season_year, get_user_starters_points, get_user_matchup
from state_manager import load_state, save_state, compare_score_changes
from players_tools import Players, player_ownership_ratio, get_player_name, get_player_info


def standings_alert(league: League) -> str:
    """
    Generate a formatted message with the current league standings.

    Args:
        league (sleeper_wrapper.League): The Sleeper League instance.

    Returns:
        str: A formatted message showing the current standings with wins and losses.

    Notes:
        - Uses `display_standings` to retrieve team names, wins, and losses.
        - Teams are listed in ranking order starting from 1.
    """
    standings = display_standings(league)  # standings with wins and losses columns
    standings_message = "🏆 *Current Standings:*\n"

    for i, team in enumerate(standings, start=1):
        standings_message += f"{i}. {team['name']} ({team['wins']}-{team['losses']})\n"

    return standings_message


def matchups_alert(league: League, week: int) -> str:
    """
    Generate a formatted message with the matchup results for a given week.

    Args:
        league (League): The Sleeper League instance.
        week (int): The week number to retrieve matchups for.

    Returns:
        str: A formatted message showing the results of each matchup for the given week.

    Notes:
        - Uses `get_scoreboards_json` to retrieve team names and scores.
        - Each matchup is displayed as `Team A points - Team B points`.
    """
    rosters = league.get_rosters()
    matchups = league.get_matchups(week)
    users = league.get_users()
    scoreboard = get_scoreboards_json(
        league=league,
        rosters=rosters,
        matchups=matchups,
        users=users
    )

    results_message = f"⚔️ *Week {week} Results:*\n"
    for match in scoreboard:
        results_message += (
            f"{match['team_a_name']} {match['team_a_points']} "
            f"- {match['team_b_points']} {match['team_b_name']}\n"
        )

    return results_message


def player_drop_alert(
    league: "League",
    week: int,
    treshold: int = 70
) -> str:
    """
    Generate an alert message for players who were dropped during the week
    but have high ownership percentage in fantasy leagues.

    Args:
        league (League): The fantasy league instance.
        week (int): The week number to check for dropped players.
        treshold (int, optional): Ownership percentage threshold to trigger an alert. Default is 70.

    Returns:
        str: A formatted message listing dropped players exceeding the ownership threshold.
             Returns an empty string if no players meet the criteria.
    """
    drops: List[str] = get_weekly_drops(league, week)
    message: str = ""

    if not drops:
        return message

    players = Players()
    season_type = "regular"
    season = get_season_year()

    player_message_data: List[Dict[str, str]] = []

    # Gather info for each dropped player
    for pid in drops:
        player_ownership = player_ownership_ratio(
            players=players,
            player_id=pid,
            season_type=season_type,
            season=season,
            week=week
        )

        owned_ratio = player_ownership.get("owned", 0)

        # Only include players exceeding the ownership threshold
        if owned_ratio > treshold:
            player_info: Dict[str, Any] = get_player_info(
                player_id=pid,
                info=['full_name', 'injury_status'],
                players=players
            )

            if not player_info["injury_status"]:
                player_info["injury_status"] = "Helthly"
            player_message_data.append(
                {
                    "name": player_info["full_name"],
                    "injury_status": player_info["injury_status"],
                    "owned": player_ownership.get("owned", 0),
                    "started": player_ownership.get("started", 0),
                }
            )

    # Build the alert message
    for player in player_message_data:
        message += (
            f"The player {player['name']} who is {player['owned']}% owned "
            f"and {player['started']}% started was dropped.His injury status is current: {player['injury_status']}\n"
        )

    return message


def weekly_alerts(league: League, last_week: int) -> List[Dict[str, str]]:
    """
    Generate weekly alert messages including standings and matchup results.

    Args:
        league (sleeper_wrapper.League): The Sleeper League instance.
        last_week (int): The most recent completed week number.

    Returns:
        List[Dict[str, str]]: A list of alert objects containing the message strings.

    Notes:
        - This function does not send messages directly.
        - It returns structured messages ready for sending via Telegram or other services.
    """
    alerts_list: List[Dict[str, str]] = []

    # --- Standings Alert ---
    standings_message = standings_alert(league)
    alerts_list.append({"message": standings_message})

    # --- Matchups / Results Alert ---
    matchups_message = matchups_alert(league, last_week)
    alerts_list.append({"message": matchups_message})

    return alerts_list


def daily_alerts(league, last_week: int):
    alerts_list = []
    transactions = fetch_all_transactions(league, last_week)
    for tx in transactions:
        if tx["type"] in ["drop", "waiver"]:
            for player in tx.get("players", []):
                if player.get("ownership", 0) >= 70:
                    alerts_list.append({
                        "player_id": player["player_id"],
                        "ownership": player["ownership"],
                        "type": tx["type"],
                        "week": tx.get("week")
                    })
    send_alerts(alerts_list)
    return alerts_list


def within_valid_hours() -> bool:
    tz = pytz.timezone("Europe/Lisbon")
    now = datetime.now(tz)
    weekday = now.weekday()  # Monday=0
    return (
        (weekday == 3 and now.hour >= 20) or (weekday == 4 and now.hour < 5) or  # Thu-Fri
        (weekday == 6 and now.hour >= 14) or (weekday == 0 and now.hour < 5) or  # Sun-Mon
        (weekday == 0 and now.hour >= 20) or (weekday == 1 and now.hour < 5)     # Mon-Tue
    )


def live_score_change_alert(league: League, user_id: str, week: int) -> List[Dict[str, str]]:
    """
    Check if the user's team scored >5 points since the last check
    and identify which player(s) contributed to the increase.

    Args:
        league (League): The Sleeper league instance.
        user_id (str): The Sleeper user ID.
        week (int): The week number to retrieve matchups for.

    Returns:
        List[Dict[str, str]]: List of alert messages for Telegram bot.
    """

    if not within_valid_hours():
        return []

    alerts: List[Dict[str, str]] = []
    state = load_state()

    matchups = league.get_matchups(week)
    user_matchup = get_user_matchup(league, user_id, matchups)

    total_points = user_matchup['points']

    prev_user_state = state.get(user_id)

    # First run: initialize state and exit
    if not prev_user_state:
        state[user_id] = {
            "timestamp": datetime.now().isoformat(),
            "players": {},
            "total_points": 0
        }
        save_state(state)
        return []

    prev_total = prev_user_state.get("total_points", 0.0)

    if prev_total == total_points:
        return []

    current_data = get_user_starters_points(league, user_id, matchups)

    diff = total_points - prev_total

    if diff > 5:
        # Identify which players' points changed
        changed_players = []
        for pid, pdata in current_data.items():
            prev_points = prev_user_state["players"].get(pid, {}).get("points", 0.0)
            delta = pdata["points"]-prev_points
            if delta > 0:
                changed_players.append(f"{pdata['name']} (+{delta:.2f})")

        if changed_players:
            message = (
                f"🔥 Your team scored +{diff:.2f} points!\n"
                f"Scoring players: {', '.join(changed_players)}"
            )
            alerts.append({"message": message})

    # Update state
    state[user_id] = {
        "timestamp": datetime.now().isoformat(),
        "players": current_data,
        "total_points": total_points
    }
    save_state(state)

    if alerts:
        send_alerts(alerts)
    return alerts

def format_score_alert_message(diff_info: Dict[str, any]) -> str:
    total_diff = diff_info["total_diff"]
    players = diff_info["changed_players"]
    if not players:
        return ""
    return (
        f"🔥 *Your team scored +{total_diff:.2f} points!*\n"
        f"Players contributing: {', '.join(players)}"
    )

