"""
league_tools.py

Utilities for interacting with a Sleeper league.
Includes fetching last played week, matchups, transactions,
standings, and alerts for high-owned dropped/waiver players.
"""

import datetime
import json
from sleeper_wrapper import League
from players_tools import get_player_info
from typing import List, Dict, Any
import os
from datetime import datetime


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


def get_scoreboards_json(
        league: League,
        rosters: List[Dict],
        matchups: List[Dict],
        users: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Returns the scoreboard in a JSON-friendly format.

    Args:
        league (League): League variable from Sleeper API
        rosters (List[Dict]): List of roster objects from Sleeper API.
        matchups (List[Dict]): List of matchup objects from Sleeper API.
        users (List[Dict]): List of user objects from Sleeper API.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a matchup with:
            - matchup_id (int)
            - team_a_name (str)
            - team_a_points (float)
            - team_b_name (str)
            - team_b_points (float)

    Notes:
        - Uses get_scoreboards() internally to preserve original logic.
        - If there is a matchup with only one team (e.g., bye week), team_b fields will be None.
    """
    raw_scoreboards = league.get_scoreboards(rosters, matchups, users)
    if not raw_scoreboards:
        return []

    json_friendly_list = []
    for matchup_id, teams in raw_scoreboards.items():
        team_a_name = teams[0][0]
        team_a_points = teams[0][1]
        if len(teams) > 1:
            team_b_name = teams[1][0]
            team_b_points = teams[1][1]
        else:
            team_b_name = None
            team_b_points = None

        json_friendly_list.append({
            "matchup_id": matchup_id,
            "team_a_name": team_a_name,
            "team_a_points": team_a_points,
            "team_b_name": team_b_name,
            "team_b_points": team_b_points
        })

    return json_friendly_list


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


def get_user_roster(user_id: str, league: League) -> Dict:
    """
    Retrieve the roster dictionary for a specific user.

    Args:
        user_id (str): The ID of the user.
        league (League): League object with the league information

    Returns:
        Dict: The roster dictionary for the given user.

    Raises:
        ValueError: If the user_id is not found in any roster.
    """
    rosters: List[Dict] = league.get_rosters()
    for roster in rosters:
        if roster['owner_id'] == user_id:
            return roster
    raise ValueError(f"user_id '{user_id}' wasn't found in any rosters")


# def get_starters_ids(user_id: str, rosters: List[Dict]) -> List[str]:
#     """
#     Get the list of starter player IDs for a given user.
#
#     Args:
#         user_id (str): The ID of the user.
#         rosters (List[Dict]): List of rosters, each containing 'owner_id' and 'starters'.
#
#     Returns:
#         List[str]: List of starter player IDs for the user.
#     """
#     roster = get_user_roster(user_id, rosters)
#     return roster['starters']


def get_user_matchup(league: League, user_id: str, matchups: List[Dict]) -> Dict[str, Any]:
    """
    Retrieve the matchup information for a specific user in a given week.

    Args:
        league (League): The Sleeper League instance containing rosters and matchup data.
        user_id (str): The unique Sleeper user ID to identify which team to locate.
        matchups (List[Dict[str, Any]]): A list of matchup dictionaries for the week,
            each containing keys such as 'roster_id', 'players_points', and 'starters'.

    Returns:
        Dict[str, Any]: The matchup dictionary corresponding to the user's roster,
        including roster ID, starters, and points.

    Raises:
        ValueError: If the user_id is not found in the league rosters or
        if the corresponding matchup for that roster cannot be located.
    """

    roster = get_user_roster(user_id, league)
    roster_id = roster['roster_id']

    # Find the matchup for this roster
    for matchup in matchups:
        if matchup['roster_id'] == roster_id:
            return matchup

    raise ValueError(f"No matchup found for user_id '{user_id}' with roster_id '{roster_id}'.")


def get_user_starters_points(league: League, user_id: str, matchups: List[Dict]) -> Dict[str, Dict[str, object]]:
    """
    Get the points and names of starter players for a given user.

    Args:
        league (League): League object with the league information
        user_id (str): The ID of the user.
        matchups (List[Dict]): List of matchups, each containing 'roster_id', 'starters', and 'players_points'.

    Returns:
        Dict[str, Dict[str, object]]: Dictionary where keys are player IDs and values are dictionaries with
                                      'name' (player full name) and 'points'.

    Raises:
        ValueError: If the user_id is not found in any roster or if players_points for the roster isn't found.
    """
    matchup = get_user_matchup(league=league, user_id=user_id, matchups=matchups)
    starters_ids = matchup["starters"]

    all_players_points = matchup['players_points']

    # Keep only starter players and attach full name
    players_points = {
        player_id: {
            "name": get_player_info(player_id, "full_name"),
            "points": all_players_points[player_id]
        }
        for player_id in starters_ids if player_id in all_players_points
    }

    if players_points:
        return players_points
    else:
        raise ValueError(f"No players_points found for user_id '{user_id}'")


def get_weekly_drops(league: League, week: int) -> List[str]:
    """
       Retrieve all players who were dropped during a given week
       and are still available (i.e., were not subsequently added again).

       Args:
           league (League): The fantasy league instance providing transaction data.
           week (int): The week number to check transactions for.

       Returns:
           List[str]: A list of player IDs (or names) that were dropped
                      and not re-added during the same week.
    """
    transactions: List[Dict[str, Any]] = league.get_transactions(week)

    dropped_players: set = set()

    for player_transaction in transactions:
        dropped: Dict[str, int] = player_transaction.get("drops", None)
        added: Dict[str, int] = player_transaction.get("adds", None)
        if dropped:
            dropped_players.update(dropped.keys())

        if added:
            for added_player in added:
                dropped_players.discard(added_player)

    return list(dropped_players)


def get_season_year() -> int:
    """
    Determine the season year based on the current month.

    If the current month is between March (3) and December (12), return the current year.
    Otherwise (January or February), return the previous year.

    Returns:
        int: The season year as an integer.
    """
    current_date = datetime.now()  # Get the current date and time
    current_year = current_date.year
    current_month = current_date.month

    # If the month is March (3) through December (12), fiscal year is the current year
    if 3 <= current_month <= 12:
        return current_year
    # If the month is January or February, fiscal year is the previous year
    else:
        return current_year - 1