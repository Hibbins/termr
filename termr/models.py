from dataclasses import dataclass
from typing import Optional
import json
from pathlib import Path


@dataclass
class RadioStation:
    id: str
    name: str
    url: str
    bitrate: int
    codec: str
    country: str
    language: str
    tags: str
    favicon: str
    votes: int
    click_count: int


@dataclass
class PlaybackStatus:
    station: Optional[RadioStation] = None
    is_playing: bool = False
    is_paused: bool = False
    current_time: float = 0.0
    metadata: Optional[dict] = None


class FavoritesManager:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.favorites_file = config_dir / "favorites.json"
        self.favorites: set[str] = set()
        self._load_favorites()

    def _load_favorites(self) -> None:
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, "r") as f:
                    data = json.load(f)
                    self.favorites = set(data.get("favorites", []))
            except (json.JSONDecodeError, IOError):
                self.favorites = set()

    def _save_favorites(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.favorites_file, "w") as f:
                json.dump({"favorites": list(self.favorites)}, f)
        except IOError:
            pass

    def add_favorite(self, station_id: str) -> None:
        self.favorites.add(station_id)
        self._save_favorites()

    def remove_favorite(self, station_id: str) -> None:
        self.favorites.discard(station_id)
        self._save_favorites()

    def is_favorite(self, station_id: str) -> bool:
        return station_id in self.favorites

    def get_favorites(self) -> set[str]:
        return self.favorites.copy()
