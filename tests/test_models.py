"""Tests for models module."""

from pathlib import Path
import tempfile

from termr.models import RadioStation, PlaybackStatus, FavoritesManager


def test_radio_station_creation():
    """Test RadioStation creation."""
    station = RadioStation(
        id="test-id",
        name="Test Station",
        url="http://example.com/stream",
        bitrate=128,
        codec="MP3",
        country="Sweden",
        language="Swedish",
        tags="test,radio",
        favicon="http://example.com/icon.png",
        votes=10,
        click_count=100
    )
    
    assert station.id == "test-id"
    assert station.name == "Test Station"
    assert station.bitrate == 128
    assert station.codec == "MP3"


def test_playback_status_defaults():
    """Test PlaybackStatus default values."""
    status = PlaybackStatus()
    
    assert status.station is None
    assert status.is_playing is False
    assert status.is_paused is False
    assert status.current_time == 0.0
    assert status.metadata is None


def test_favorites_manager():
    """Test FavoritesManager functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        manager = FavoritesManager(config_dir)
        
        assert manager.get_favorites() == set()
        assert manager.is_favorite("test-id") is False
        
        manager.add_favorite("test-id")
        assert manager.is_favorite("test-id") is True
        assert "test-id" in manager.get_favorites()
        
        manager.remove_favorite("test-id")
        assert manager.is_favorite("test-id") is False
        assert "test-id" not in manager.get_favorites()


def test_favorites_persistence():
    """Test that favorites are saved and loaded correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        
        manager1 = FavoritesManager(config_dir)
        manager1.add_favorite("test-id-1")
        manager1.add_favorite("test-id-2")
        
        manager2 = FavoritesManager(config_dir)
        assert manager2.is_favorite("test-id-1") is True
        assert manager2.is_favorite("test-id-2") is True
        assert len(manager2.get_favorites()) == 2
