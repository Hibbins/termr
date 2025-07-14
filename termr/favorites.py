from pathlib import Path
import json
from typing import Set, List, Dict, Any
from .models import RadioStation


class FavoritesManager:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.favorites_file = config_dir / "favorites.json"
        self.favorites: Dict[str, Dict[str, Any]] = {}
        self._load_favorites()

    def _load_favorites(self) -> None:
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, "r") as f:
                    data = json.load(f)
                    favorites_data = data.get("favorites", {})
                    if isinstance(favorites_data, dict):
                        self.favorites = favorites_data
                    else:
                        self.favorites = {}
            except (json.JSONDecodeError, IOError):
                self.favorites = {}

    def _save_favorites(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.favorites_file, "w") as f:
                json.dump({"favorites": self.favorites}, f)
        except IOError:
            pass

    def add_favorite(self, station: RadioStation) -> None:
        self.favorites[station.id] = {
            "id": station.id,
            "name": station.name,
            "url": station.url,
            "country": station.country,
            "bitrate": station.bitrate,
            "codec": station.codec,
            "favicon": station.favicon,
            "language": station.language,
            "tags": station.tags,
            "votes": station.votes,
            "click_count": station.click_count
        }
        self._save_favorites()

    def remove_favorite(self, station_id: str) -> None:
        self.favorites.pop(station_id, None)
        self._save_favorites()

    def is_favorite(self, station_id: str) -> bool:
        return station_id in self.favorites

    def get_favorites(self) -> List[RadioStation]:
        stations = []
        for station_data in self.favorites.values():
            station = RadioStation(
                id=station_data["id"],
                name=station_data["name"],
                url=station_data["url"],
                country=station_data["country"],
                bitrate=station_data["bitrate"],
                codec=station_data["codec"],
                favicon=station_data.get("favicon"),
                language=station_data.get("language", ""),
                tags=station_data.get("tags", ""),
                votes=station_data.get("votes", 0),
                click_count=station_data.get("click_count", 0)
            )
            stations.append(station)
        return stations

    def get_favorite_ids(self) -> Set[str]:
        return set(self.favorites.keys())

    def ensure_migration(self, api=None):
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, "r") as f:
                    data = json.load(f)
                    favorites_data = data.get("favorites", {})
                    if isinstance(favorites_data, list):
                        self.migrate_old_favorites(api=api)
            except (json.JSONDecodeError, IOError):
                pass

    def get_favorite_ids(self) -> Set[str]:
        return set(self.favorites.keys())

    def migrate_old_favorites(self, api=None):
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, "r") as f:
                    data = json.load(f)
                    favorites_data = data.get("favorites", {})
                    if isinstance(favorites_data, list):
                        id_list = list(favorites_data)
                        self.favorites = {}
                        for station_id in id_list:
                            station_obj = None
                            if api is not None:
                                try:
                                    station_obj = api.get_station_by_id(station_id)
                                except Exception:
                                    station_obj = None
                            if station_obj:
                                self.favorites[station_id] = {
                                    "id": station_obj.id,
                                    "name": station_obj.name,
                                    "url": station_obj.url,
                                    "country": station_obj.country,
                                    "bitrate": station_obj.bitrate,
                                    "codec": station_obj.codec,
                                    "favicon": station_obj.favicon,
                                    "language": station_obj.language,
                                    "tags": station_obj.tags,
                                    "votes": station_obj.votes,
                                    "click_count": station_obj.click_count
                                }
                            else:
                                self.favorites[station_id] = {
                                    "id": station_id,
                                    "name": f"Station {station_id}",
                                    "url": "",
                                    "country": "Unknown",
                                    "bitrate": 0,
                                    "codec": "Unknown",
                                    "favicon": "",
                                    "language": "",
                                    "tags": "",
                                    "votes": 0,
                                    "click_count": 0
                                }
                        self._save_favorites()
            except Exception:
                pass
