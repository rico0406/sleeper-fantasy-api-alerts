from sleeper_wrapper import Players
from typing import Optional, Union, List, Tuple, Any, Dict


def get_player_info(
    player_id: str,
    info: Union[str, List[str], Tuple[str, ...]],
    players: Optional[Players] = None
) -> Union[str, Dict[str, Any]]:
    """
    Retrieve specific information about a player from the Sleeper API by their player ID.

    Args:
        player_id (str): The unique ID of the player.
        info (Union[str, List[str], Tuple[str, ...]]):
            Name of the information to retrieve (e.g., 'full_name') or a list/tuple of info names.
        players (Optional[Players]): Instance of Players class containing all players.
                                     If None, a new instance will be created.

    Returns:
        Union[str, Dict[str, Any]]:
            - If `info` is a string, returns the value of that field.
            - If `info` is a list/tuple of strings, returns a dictionary with key-value pairs.

    Raises:
        TypeError:
            - If `player_id` is not a string.
            - If `info` is not a string, list, or tuple of strings.
        KeyError:
            - If the `player_id` does not exist.
            - If any requested info key does not exist for the player, specifies which key(s) are invalid.
    """
    # --- Input validation ---
    if not isinstance(player_id, str):
        raise TypeError(f"player_id must be a string, got {type(player_id).__name__}")

    if not isinstance(info, (str, list, tuple)):
        raise TypeError(f"info must be a string, list, or tuple of strings, got {type(info).__name__}")

    # If info is list/tuple, ensure all elements are strings
    if isinstance(info, (list, tuple)):
        if not all(isinstance(i, str) for i in info):
            raise TypeError("All elements in info list/tuple must be strings")

    # --- Ensure we have a Players instance ---
    if not players:
        players = Players()

    # --- Get all players ---
    all_players: Dict[str, Any] = players.get_all_players()

    if player_id not in all_players:
        raise KeyError(f"Player ID '{player_id}' does not exist.")

    player_data = all_players[player_id]

    # --- Convert single string info to list for uniform processing ---
    if isinstance(info, str):
        info_keys = [info]
        single_return = True
    else:
        info_keys = list(info)
        single_return = False

    #--- Add team name if it is a DST---
    if player_data.get("position", "") == "DEF" and info=="full_name":
        player_data[info] = f"{player_data['first_name']} {player_data['last_name']}"
    # --- Check for missing keys ---
    missing_keys = [key for key in info_keys if key not in player_data]
    if missing_keys:
        print(player_data)
        raise KeyError(f"Invalid info key(s) for player {player_id}: {missing_keys}")

    # --- Gather requested info ---
    result = {key: player_data[key] for key in info_keys}

    # --- Return single value if input was a string ---
    if single_return:
        return result[info]
    return result


def get_player_name(player_id: str, players: Optional[Players] = None) -> str:
    """
    Retrieve the full name of a player from Sleeper API by their player ID.

    Args:
        player_id (str): The unique ID of the player.
        players (Optional[Players]): Instance of players class with all the players.

    Returns:
        str: Full name of the player in the format 'FirstName LastName'.

    Raises:
        KeyError: If the player_id does not exist in the list of all players.
    """
    # Get all players as a dictionary where key is player_id and value is player info
    if not players:
        players: Players = Players()

    all_players = players.get_all_players()

    # Retrieve the player information for the given player_id
    player: dict = all_players[player_id]

    # Return the full name

    return player['full_name']


def player_ownership_ratio(
        player_id: str,
        season_type: str,
        season: int,
        players: Players | None = None,
        week: int | None = None
):
    if not players:
        players: Players = Players()

    players_ratio: Dict[str, Dict[str, str]] = players.get_players_ownership(
        season_type=season_type,
        season=season,
        week=week
    )
    return players_ratio[player_id]
