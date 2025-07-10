import json
from pathlib import Path
from typing import Dict, Any


class Config:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "settings.json"
        self.settings = self._load_default_settings()
        self._load_settings()

        if "volume" not in self.settings:
            self.set("volume", 100)

    def _load_default_settings(self) -> Dict[str, Any]:
        return {
            "max_stations": 100,
            "default_sort": "clickcount",
            "auto_play": False,
            "volume": 100,
            "theme": "default",
            "last_station": None,
            "api_timeout": 10,
        }

    def _load_settings(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_settings(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self._save_settings()

    def get_all(self) -> Dict[str, Any]:
        return self.settings.copy()
