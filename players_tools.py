from sleeper_wrapper import Players
from typing import Dict


def get_player_name(player_id: str) -> str:
    """
    Retrieve the full name of a player from Sleeper API by their player ID.

    Args:
        player_id (str): The unique ID of the player.

    Returns:
        str: Full name of the player in the format 'FirstName LastName'.

    Raises:
        KeyError: If the player_id does not exist in the list of all players.
    """
    # Get all players as a dictionary where key is player_id and value is player info
    all_players: Dict[str, dict] = Players().get_all_players()

    # Retrieve the player information for the given player_id
    player: dict = all_players[player_id]

    # Construct the full name by combining first and last name
    name: str = f"{player['first_name']} {player['last_name']}"

    return name
