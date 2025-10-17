"""
league_tools.py

Utilities for interacting with a Sleeper league.
Includes fetching last played week, matchups, transactions,
standings, and alerts for high-owned dropped/waiver players.
"""

import datetime
import json
from sleeper_wrapper import League
from typing import List, Dict
import os
import requests


def get_max_weeks_by_month() -> int:
    """
    Estimate the maximum number of weeks based on the current month,
    assuming the league starts in September.

    Returns:
        int: Maximum number of weeks to check.
    """
    month = datetime.datetime.now().month
    if month == 9:
        return 6
    elif month == 10:
        return 10
    elif month == 11:
        return 14
    elif month >= 12:
        return 18
    return 18


def get_last_week_number(league: League, max_weeks: int = 18) -> int:
    """
    Determines the last week that has actual played matchups
    by checking if at least one team scored points in the week.

    Args:
        league (League): The League object representing the league.
        max_weeks (int): Maximum number of weeks to check (default 18).

    Returns:
        int: The number of the last week played.
    """
    for week in range(max_weeks, 0, -1):
        matchups = league.get_matchups(week)
        if not matchups:
            continue

        # Consider week played if any team scored points
        week_played = any(matchup.get("points", 0) > 0 for matchup in matchups)
        if week_played:
            return week
    return 1


def alert_high_owned_dropped_players(transactions: List[Dict], threshold: float = 70):
    """
    Alerts on players that are dropped or in waivers and have ownership above the threshold.

    Args:
        transactions (list): List of transactions from league.get_transactions().
        threshold (float): Ownership percentage threshold (0-100).
    """
    print(f"\n=== ALERT: Players > {threshold}% owned dropped or on waivers ===")
    for tx in transactions:
        if tx["type"] in ["drop", "waiver"]:
            for player in tx.get("players", []):
                player_id = player.get("player_id")
                ownership = player.get("ownership", 0)  # Ownership comes from API
                if ownership >= threshold:
                    print(f"Player ID {player_id} | Ownership: {ownership:.1f}% | Transaction type: {tx['type']} | Week: {tx.get('week')}")


def fetch_all_transactions(league: League, last_week: int) -> List[Dict]:
    """
    Fetch all transactions in the league up to the last played week.

    Args:
        league (League): League object.
        last_week (int): Last week played.

    Returns:
        list: List of transaction dictionaries.
    """
    all_transactions = []
    for week in range(1, last_week + 1):
        tx = league.get_transactions(week)
        if tx:
            all_transactions.extend(tx)
    return all_transactions


def display_matchups(league: League, week: int):
    """
    Fetch and print matchups for a given week.

    Args:
        league (League): League object.
        week (int): Week number.
    """
    matchups = league.get_matchups(week)

    # Converting to dict
    matchups_dict = [
        {
            "name": team[0],
            "wins": int(team[1]),
            "losses": int(team[2]),
            "PF": int(team[3])
        } for team in matchups
    ]

    return matchups_dict


def display_standings(league: League):
    """
    Fetch and print standings of the league.

    Args:
        league (League): League object.
    """
    rosters = league.get_rosters()
    users = league.get_users()
    standings = league.get_standings(rosters, users)

    # Converting to dict
    standings_dict = [
            {
                "name": team[0],
                "wins": int(team[1]),
                "losses": int(team[2]),
                "PF": int(team[3])
            } for team in standings
        ]

    return standings_dict

def save_league_data_to_json(
    league_info: Dict,
    matchups: List[Dict],
    transactions: List[Dict],
    standings: List[Dict],
    alerts: List[Dict],
    output_dir: str = "data"
):
    """
    Save league data and alerts to a JSON file.

    Args:
        league_info (dict): League information.
        matchups (list): Matchups of the last week.
        transactions (list): All transactions up to last week.
        standings (list): Current standings.
        alerts (list): List of high-owned dropped/waiver player alerts.
        output_dir (str): Directory to save JSON files.
    """
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"league_data_{timestamp}.json")

    data = {
        "league_info": league_info,
        "matchups": matchups,
        "transactions": transactions,
        "standings": standings,
        "alerts": alerts,
        "timestamp": timestamp
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"\nLeague data saved to {filename}")


def get_player_stats(player_id, date):
    """
    Fetch player stats from Sleeper for a given date (YYYY-MM-DD)
    """
    url = f"https://api.sleeper.app/v1/stats/nfl/regular/{date}"
    response = requests.get(url)
    if response.status_code != 200:
        return {}
    stats_data = response.json()  # dict {player_id: stats}
    return stats_data.get(player_id, {})