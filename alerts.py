from datetime import datetime
from telegram_bot import send_alerts
from league_tools import fetch_all_transactions, display_standings


def weekly_alerts(league, last_week: int):
    """
    Send weekly alerts: standings and results of matchups.
    Returns a list of alerts for further processing.
    """
    alerts_list = []

    # --- 1️⃣ Standings ---
    standings = display_standings(league)  # lista de times com wins/losses
    standings_message = "🏆 *Current Standings:*\n"

    for i, team in enumerate(standings, start=1):
        print(team)
        standings_message += f"{i}. {team['name']} ({team['wins']}-{team['losses']})\n"
    alerts_list.append({"message": standings_message})

    # --- 2️⃣ Matchups / Results ---
    matchups = league.get_matchups(week=last_week)  # lista de jogos da semana
    results_message = f"⚔️ *Week {last_week} Results:*\n"
    for matchup in matchups:
        home = matchup['home_team']
        away = matchup['away_team']
        results_message += f"{home['name']} {home['points']} - {away['points']} {away['name']}\n"
    alerts_list.append({"message": results_message})

    league.get_scoreboards()

    # --- Return the alerts list (sending via Telegram can be done separately) ---
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
