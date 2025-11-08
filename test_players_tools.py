import pytest
from unittest.mock import patch
from players_tools import get_player_name


@pytest.fixture
def mock_players_data():
    return {
        "123": {"first_name": "Patrick", "last_name": "Mahomes"},
        "456": {"first_name": "Josh", "last_name": "Allen"},
    }


@patch("players_tools.Players")
def test_get_player_name_valid(mock_players_class, mock_players_data):
    """Test that get_player_name returns the correct full name."""
    mock_instance = mock_players_class.return_value
    mock_instance.get_all_players.return_value = mock_players_data

    result = get_player_name("123")
    assert result == "Patrick Mahomes"


@patch("players_tools.Players")
def test_get_player_name_different_player(mock_players_class, mock_players_data):
    """Test getting another player's name."""
    mock_instance = mock_players_class.return_value
    mock_instance.get_all_players.return_value = mock_players_data

    result = get_player_name("456")
    assert result == "Josh Allen"


@patch("players_tools.Players")
def test_get_player_name_invalid_id(mock_players_class, mock_players_data):
    """Test that function raises KeyError if player_id does not exist."""
    mock_instance = mock_players_class.return_value
    mock_instance.get_all_players.return_value = mock_players_data

    with pytest.raises(KeyError):
        get_player_name("999")


@patch("players_tools.Players")
def test_get_player_name_missing_field(mock_players_class):
    """Test behavior when player data is missing name fields."""
    mock_instance = mock_players_class.return_value
    mock_instance.get_all_players.return_value = {
        "789": {"first_name": "Incomplete"}  # Missing last_name
    }

    with pytest.raises(KeyError):
        get_player_name("789")
