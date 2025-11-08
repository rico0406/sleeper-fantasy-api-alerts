from sleeper_wrapper import Players
from typing import Dict


def get_player_name(player_id: str) -> str:

    all_players: dict = Players().get_all_players()
    player: dict = all_players[player_id]
    name: str = f"{player['first_name']} {player['last_name']}"
    return name
