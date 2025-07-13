"""Tests for Textual UI components."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from textual.app import App

from termr.ui import TermrApp, StationList
from termr.models import RadioStation


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config_dir(temp_config_dir):
    """Mock the config directory to use temporary directory."""
    with patch.object(TermrApp, 'get_config_dir', return_value=temp_config_dir):
        yield temp_config_dir


@pytest.fixture
def sample_stations():
    """Create sample radio stations for testing."""
    return [
        RadioStation(
            id="station-1",
            name="Test Station 1",
            url="http://example.com/stream1",
            bitrate=128,
            codec="MP3",
            country="Sweden",
            language="Swedish",
            tags="test,radio",
            favicon="http://example.com/icon1.png",
            votes=10,
            click_count=100
        ),
        RadioStation(
            id="station-2",
            name="Test Station 2",
            url="http://example.com/stream2",
            bitrate=256,
            codec="AAC",
            country="Norway",
            language="Norwegian",
            tags="music,pop",
            favicon="http://example.com/icon2.png",
            votes=20,
            click_count=200
        )
    ]


def test_station_list_initialization():
    """Test StationList initialization."""
    station_list = StationList()
    
    assert station_list.stations == []
    assert station_list.get_selected_station() is None


@patch('termr.ui.StationList.app')
def test_station_list_populate(mock_app, sample_stations):
    """Test populating station list."""
    mock_app.favorites_manager.is_favorite.return_value = False
    station_list = StationList()
    station_list.on_mount()  # Add columns first
    station_list.load_stations(sample_stations)
    
    assert len(station_list.stations) == 2
    assert station_list.stations[0].name == "Test Station 1"
    assert station_list.stations[1].name == "Test Station 2"


@patch('termr.ui.StationList.app')
def test_station_list_get_selected(mock_app, sample_stations):
    """Test getting selected station."""
    mock_app.favorites_manager.is_favorite.return_value = False
    station_list = StationList()
    station_list.on_mount()  # Add columns first
    station_list.load_stations(sample_stations)
    
    # After loading stations, first station should be selected
    selected = station_list.get_selected_station()
    assert selected is not None
    assert selected.name == "Test Station 1"


@patch('termr.ui.StationList.app')
def test_station_list_populate_method(mock_app, sample_stations):
    """Test populating station list using load_stations method."""
    mock_app.favorites_manager.is_favorite.return_value = False
    station_list = StationList()
    station_list.on_mount()  # Add columns first
    station_list.load_stations(sample_stations)
    
    assert len(station_list.stations) == 2
    assert station_list.stations[0].name == "Test Station 1"
    assert station_list.stations[1].name == "Test Station 2"


@patch('termr.ui.TermrApp.run')
def test_termr_app_initialization(mock_run, mock_config_dir):
    """Test TermrApp initialization."""
    app = TermrApp()
    
    assert app.stations == []
    assert app.favorites_manager is not None
    assert app._active_theme == "default"


def test_termr_app_theme_application(mock_config_dir):
    """Test theme application."""
    app = TermrApp()
    
    # Test applying different themes
    app.apply_theme("monokai")
    assert app._active_theme == "monokai"
    
    app.apply_theme("dracula")
    assert app._active_theme == "dracula"
    
    app.apply_theme("light")
    assert app._active_theme == "light"


def test_termr_app_invalid_theme(mock_config_dir):
    """Test handling of invalid theme."""
    app = TermrApp()
    original_theme = app._active_theme
    
    # Should not change theme for invalid name
    app.apply_theme("invalid_theme")
    assert app._active_theme == original_theme


def test_termr_app_view_switching(mock_config_dir):
    """Test switching between views."""
    app = TermrApp()
    
    # Test that app can be initialized without errors
    assert app is not None
    assert hasattr(app, 'show_station_list')
    assert hasattr(app, 'show_favorites_list')
    assert hasattr(app, 'show_help_screen')
    assert hasattr(app, 'show_theme_screen')
