import json
import os
from typing import Dict, Any, List

STATE_FILE = "data/live_state.json"


def load_state() -> Dict[str, Any]:
    """
    Load the previous alert state from disk.

    Returns:
        Dict[str, Any]: The stored state for all users.
    """
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: Dict[str, Any]) -> None:
    """
    Persist the current alert state to disk.

    Args:
        state (Dict[str, Any]): The state dictionary to be saved.
    """
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def compare_score_changes(prev_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two user score states and return differences.

    Args:
        prev_state (Dict[str, Any]): Previous state with player scores and totals.
        current_state (Dict[str, Any]): Current state snapshot.

    Returns:
        Dict[str, Any]: {
            "total_diff": float,
            "changed_players": [ "PlayerName (+X.XX)", ... ]
        }
    """
    total_diff = current_state["total_points"] - prev_state.get("total_points", 0.0)

    changed_players: List[str] = []
    for pid, pdata in current_state["players"].items():
        prev_points = prev_state["players"].get(pid, {}).get("points", 0.0)
        delta = pdata["points"] - prev_points
        if delta > 0:
            changed_players.append(f"{pdata['name']} (+{delta:.2f})")

    return {"total_diff": total_diff, "changed_players": changed_players}
