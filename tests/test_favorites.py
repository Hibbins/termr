"""Tests for favorites management and migration."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from termr.favorites import FavoritesManager
from termr.models import RadioStation


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_station():
    """Create a sample radio station for testing."""
    return RadioStation(
        id="test-station-1",
        name="Test Station",
        url="http://example.com/stream",
        country="Sweden",
        bitrate=128,
        codec="MP3",
        favicon="http://example.com/icon.png",
        language="Swedish",
        tags="test,radio",
        votes=10,
        click_count=100
    )


@pytest.fixture
def mock_api(sample_station):
    """Create a mock API for testing."""
    api = Mock()
    api.get_station_by_id.return_value = sample_station
    return api


def test_favorites_manager_initialization(temp_config_dir):
    """Test FavoritesManager initialization."""
    manager = FavoritesManager(temp_config_dir)
    assert manager.config_dir == temp_config_dir
    assert manager.favorites_file == temp_config_dir / "favorites.json"
    assert manager.favorites == {}


def test_load_favorites_new_format(temp_config_dir):
    """Test loading favorites in new format (dict)."""
    favorites_data = {
        "favorites": {
            "test-station-1": {
                "id": "test-station-1",
                "name": "Test Station",
                "url": "http://example.com/stream",
                "country": "Sweden",
                "bitrate": 128,
                "codec": "MP3",
                "favicon": "http://example.com/icon.png",
                "language": "Swedish",
                "tags": "test,radio",
                "votes": 10,
                "click_count": 100
            }
        }
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    assert "test-station-1" in manager.favorites
    assert manager.favorites["test-station-1"]["name"] == "Test Station"


def test_load_favorites_old_format(temp_config_dir):
    """Test loading favorites in old format (list) - should be empty initially."""
    favorites_data = {
        "favorites": ["test-station-1", "test-station-2"]
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    assert manager.favorites == {}


def test_migrate_old_favorites_with_api(temp_config_dir, mock_api):
    """Test migration of old favorites format with API."""
    favorites_data = {
        "favorites": ["test-station-1"]
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    manager.migrate_old_favorites(api=mock_api)
    
    assert "test-station-1" in manager.favorites
    assert manager.favorites["test-station-1"]["name"] == "Test Station"
    assert manager.favorites["test-station-1"]["country"] == "Sweden"


def test_migrate_old_favorites_without_api(temp_config_dir):
    """Test migration of old favorites format without API."""
    favorites_data = {
        "favorites": ["test-station-1", "test-station-2"]
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    manager.migrate_old_favorites()
    
    assert "test-station-1" in manager.favorites
    assert "test-station-2" in manager.favorites
    assert manager.favorites["test-station-1"]["name"] == "Station test-station-1"
    assert manager.favorites["test-station-1"]["country"] == "Unknown"


def test_migrate_old_favorites_api_error(temp_config_dir):
    """Test migration when API raises an exception."""
    favorites_data = {
        "favorites": ["test-station-1"]
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    mock_api = Mock()
    mock_api.get_station_by_id.side_effect = Exception("API Error")
    
    manager = FavoritesManager(temp_config_dir)
    manager.migrate_old_favorites(api=mock_api)
    
    assert "test-station-1" in manager.favorites
    assert manager.favorites["test-station-1"]["name"] == "Station test-station-1"


def test_migration_writes_new_format_to_file(temp_config_dir, mock_api):
    """Test that migration actually writes the new dict format to favorites.json file."""
    favorites_data = {
        "favorites": ["test-station-1"]
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    manager.migrate_old_favorites(api=mock_api)
    
    # Verify the file was actually rewritten with new format
    with open(temp_config_dir / "favorites.json", "r") as f:
        file_content = json.load(f)
    
    assert "favorites" in file_content
    assert isinstance(file_content["favorites"], dict)
    assert "test-station-1" in file_content["favorites"]
    assert file_content["favorites"]["test-station-1"]["name"] == "Test Station"
    assert file_content["favorites"]["test-station-1"]["country"] == "Sweden"


def test_ensure_migration_triggers_migration(temp_config_dir, mock_api):
    """Test that ensure_migration triggers migration for old format."""
    favorites_data = {
        "favorites": ["test-station-1"]
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    manager.ensure_migration(api=mock_api)
    
    assert "test-station-1" in manager.favorites
    assert manager.favorites["test-station-1"]["name"] == "Test Station"


def test_ensure_migration_no_migration_needed(temp_config_dir):
    """Test that ensure_migration doesn't trigger migration for new format."""
    favorites_data = {
        "favorites": {
            "test-station-1": {
                "id": "test-station-1",
                "name": "Test Station",
                "url": "http://example.com/stream",
                "country": "Sweden",
                "bitrate": 128,
                "codec": "MP3",
                "favicon": "http://example.com/icon.png",
                "language": "Swedish",
                "tags": "test,radio",
                "votes": 10,
                "click_count": 100
            }
        }
    }
    
    with open(temp_config_dir / "favorites.json", "w") as f:
        json.dump(favorites_data, f)
    
    manager = FavoritesManager(temp_config_dir)
    initial_favorites = manager.favorites.copy()
    manager.ensure_migration()
    
    assert manager.favorites == initial_favorites


def test_add_favorite(temp_config_dir, sample_station):
    """Test adding a favorite station."""
    manager = FavoritesManager(temp_config_dir)
    manager.add_favorite(sample_station)
    
    assert sample_station.id in manager.favorites
    assert manager.favorites[sample_station.id]["name"] == sample_station.name
    assert manager.favorites[sample_station.id]["url"] == sample_station.url


def test_remove_favorite(temp_config_dir, sample_station):
    """Test removing a favorite station."""
    manager = FavoritesManager(temp_config_dir)
    manager.add_favorite(sample_station)
    manager.remove_favorite(sample_station.id)
    
    assert sample_station.id not in manager.favorites


def test_get_favorites(temp_config_dir, sample_station):
    """Test getting favorites as RadioStation objects."""
    manager = FavoritesManager(temp_config_dir)
    manager.add_favorite(sample_station)
    
    favorites = manager.get_favorites()
    assert len(favorites) == 1
    assert favorites[0].id == sample_station.id
    assert favorites[0].name == sample_station.name


def test_get_favorite_ids(temp_config_dir, sample_station):
    """Test getting favorite IDs."""
    manager = FavoritesManager(temp_config_dir)
    manager.add_favorite(sample_station)
    
    favorite_ids = manager.get_favorite_ids()
    assert sample_station.id in favorite_ids
    assert len(favorite_ids) == 1


def test_is_favorite(temp_config_dir, sample_station):
    """Test checking if a station is a favorite."""
    manager = FavoritesManager(temp_config_dir)
    manager.add_favorite(sample_station)
    
    assert manager.is_favorite(sample_station.id) is True
    assert manager.is_favorite("non-existent-id") is False 