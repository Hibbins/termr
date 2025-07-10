"""Tests for VLC player integration."""

import pytest
from unittest.mock import Mock, patch

from termr.player import VLCPlayer
from termr.models import RadioStation


@pytest.fixture
def sample_station():
    """Create a sample radio station for testing."""
    return RadioStation(
        id="test-station",
        name="Test Radio",
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


def test_player_initialization():
    """Test VLCPlayer initialization."""
    player = VLCPlayer()
    
    assert player.process is None
    assert player.current_station is None
    assert player.is_playing() is False


@patch('subprocess.run')
@patch('subprocess.Popen')
def test_play_station_success(mock_popen, mock_run, sample_station):
    """Test successful station playback."""
    mock_process = Mock()
    mock_process.poll.return_value = None
    mock_popen.return_value = mock_process
    mock_run.return_value.returncode = 0
    
    player = VLCPlayer()
    success = player.play(sample_station)
    
    assert success is True
    assert player.current_station == sample_station
    assert player.is_playing() is True


def test_stop_without_playing():
    """Test stopping when nothing is playing."""
    player = VLCPlayer()
    
    # Should not crash
    player.stop()
    assert player.is_playing() is False


def test_volume_control():
    """Test volume control functionality."""
    player = VLCPlayer()
    
    # Set volume
    player.set_volume(50)
    assert player.volume == 50
    
    # Volume should be clamped to 0-200
    player.set_volume(300)
    assert player.volume == 300
    
    player.set_volume(-10)
    assert player.volume == -10


def test_get_playback_status(sample_station):
    """Test getting playback status."""
    player = VLCPlayer()
    
    status = player.get_status()
    assert status.station is None
    assert status.is_playing is False
    assert status.is_paused is False
