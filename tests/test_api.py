"""Tests for Radio Browser API integration."""

import pytest
from unittest.mock import Mock, patch
import requests

from termr.api import RadioBrowserAPI


@pytest.fixture
def mock_response():
    """Mock API response."""
    mock = Mock()
    mock.json.return_value = [
        {
            "stationuuid": "test-id-1",
            "name": "Test Station 1",
            "url": "http://example.com/stream1",
            "bitrate": 128,
            "codec": "MP3",
            "country": "Sweden",
            "language": "Swedish",
            "tags": "test,radio",
            "favicon": "http://example.com/icon1.png",
            "votes": 10,
            "clickcount": 100
        },
        {
            "stationuuid": "test-id-2",
            "name": "Test Station 2",
            "url": "http://example.com/stream2",
            "bitrate": 256,
            "codec": "AAC",
            "country": "Norway",
            "language": "Norwegian",
            "tags": "music,pop",
            "favicon": "http://example.com/icon2.png",
            "votes": 20,
            "clickcount": 200
        }
    ]
    mock.status_code = 200
    return mock


def test_api_initialization():
    """Test API initialization."""
    api = RadioBrowserAPI()
    assert api.BASE_URL == "https://de1.api.radio-browser.info/json"
    assert api.timeout == 10


def test_get_stations_success(mock_response):
    """Test successful station retrieval."""
    with patch('requests.Session.get', return_value=mock_response):
        api = RadioBrowserAPI()
        stations = api.search_stations(limit=2)
        
        assert len(stations) == 2
        assert stations[0].id == "test-id-1"
        assert stations[0].name == "Test Station 1"
        assert stations[0].bitrate == 128
        assert stations[1].id == "test-id-2"
        assert stations[1].name == "Test Station 2"
        assert stations[1].bitrate == 256


def test_get_stations_api_error():
    """Test API error handling."""
    mock_error_response = Mock()
    mock_error_response.status_code = 500
    mock_error_response.raise_for_status.side_effect = requests.RequestException("API Error")
    
    with patch('requests.Session.get', return_value=mock_error_response):
        api = RadioBrowserAPI()
        stations = api.search_stations(limit=10)
        
        assert stations == []


def test_search_stations(mock_response):
    """Test station search functionality."""
    with patch('requests.Session.get', return_value=mock_response):
        api = RadioBrowserAPI()
        stations = api.search_stations("test", limit=2)
        
        assert len(stations) == 2
        assert all("test" in station.name.lower() for station in stations)


def test_get_stations_by_country(mock_response):
    """Test getting stations by country."""
    with patch('requests.Session.get', return_value=mock_response):
        api = RadioBrowserAPI()
        stations = api.get_stations_by_country("Sweden", limit=2)
        
        assert len(stations) == 2
        assert stations[0].country == "Sweden"


def test_get_stations_by_tag(mock_response):
    """Test getting stations by tag."""
    with patch('requests.Session.get', return_value=mock_response):
        api = RadioBrowserAPI()
        stations = api.get_stations_by_tag("music", limit=2)
        
        assert len(stations) == 2
        assert "music" in stations[1].tags
