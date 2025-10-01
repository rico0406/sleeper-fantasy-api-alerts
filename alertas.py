from datetime import datetime
from telegram_bot import send_alerts
from league_tools import fetch_all_transactions

def weekly_alerts(league, last_week: int):
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
