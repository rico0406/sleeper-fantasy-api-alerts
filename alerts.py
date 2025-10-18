from datetime import datetime
from typing import List, Dict

from telegram_bot import send_alerts
from league_tools import fetch_all_transactions, display_standings, League, get_scoreboards_json


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


def live_game_alerts(league, user_id: str):
    alerts_list = []
    rosters = league.get_rosters()
    user_roster = next((r for r in rosters if r["owner_id"] == user_id), None)
    if not user_roster:
        print(f"No roster found for user {user_id}")
        return []

    players = user_roster.get("players", [])
    for player_id in players:
        player_stats = league.get_player_stats(player_id, date=datetime.now().strftime("%Y-%m-%d"))
        if not player_stats:
            continue
        td = player_stats.get("touchdowns", 0)
        fumble = player_stats.get("fumbles", 0)
        interception = player_stats.get("interceptions", 0)
        if td > 0 or fumble > 0 or interception > 0:
            alerts_list.append({
                "player_id": player_id,
                "td": td,
                "fumble": fumble,
                "interception": interception
            })
    send_alerts(alerts_list)
    return alerts_list
