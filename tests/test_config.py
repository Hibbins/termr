"""Tests for configuration management."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from termr.config import Config


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_config_initialization(temp_config_dir):
    """Test Config initialization."""
    config = Config(temp_config_dir)
    
    assert config.config_dir == temp_config_dir
    assert config.config_file == temp_config_dir / "settings.json"


def test_default_settings(temp_config_dir):
    """Test default settings are loaded correctly."""
    config = Config(temp_config_dir)
    
    settings = config.get_all()
    assert settings["max_stations"] == 100
    assert settings["default_sort"] == "clickcount"
    assert settings["auto_play"] is False
    assert settings["volume"] == 100
    assert settings["theme"] == "default"
    assert settings["last_station"] is None
    assert settings["api_timeout"] == 10


def test_setting_value(temp_config_dir):
    """Test setting and getting individual values."""
    config = Config(temp_config_dir)
    
    config.set("volume", 75)
    assert config.get("volume") == 75
    
    config.set("theme", "monokai")
    assert config.get("theme") == "monokai"


def test_settings_persistence(temp_config_dir):
    """Test that settings are saved and loaded correctly."""
    config1 = Config(temp_config_dir)
    config1.set("volume", 80)
    config1.set("theme", "dracula")
    
    config2 = Config(temp_config_dir)
    assert config2.get("volume") == 80
    assert config2.get("theme") == "dracula"


def test_invalid_setting(temp_config_dir):
    """Test handling of invalid setting keys."""
    config = Config(temp_config_dir)
    
    # Should return None for invalid keys
    assert config.get("invalid_key") is None
    
    # Should not crash when setting invalid keys
    config.set("invalid_key", "value")


def test_settings_file_creation(temp_config_dir):
    """Test that settings file is created if it doesn't exist."""
    config = Config(temp_config_dir)
    
    # Set a value to trigger file creation
    config.set("test_key", "test_value")
    
    # Settings file should be created
    assert config.config_file.exists()
    
    # Should contain valid JSON
    with open(config.config_file, 'r') as f:
        data = json.load(f)
        assert isinstance(data, dict)


def test_corrupted_settings_file(temp_config_dir):
    """Test handling of corrupted settings file."""
    settings_file = temp_config_dir / "settings.json"
    
    # Create corrupted JSON file
    with open(settings_file, 'w') as f:
        f.write("invalid json content")
    
    # Should handle gracefully and use defaults
    config = Config(temp_config_dir)
    settings = config.get_all()
    assert settings["volume"] == 100  # Default value


def test_get_with_default(temp_config_dir):
    """Test getting values with default fallback."""
    config = Config(temp_config_dir)
    
    # Should return default for non-existent key
    assert config.get("non_existent", "default_value") == "default_value"
    
    # Should return actual value for existing key
    config.set("test_key", "test_value")
    assert config.get("test_key", "default_value") == "test_value"
