import requests
from typing import List
from .models import RadioStation
from .version import __version__


class RadioBrowserAPI:
    BASE_URL = "https://de1.api.radio-browser.info/json"

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"termr/{__version__}"
        })
        self.timeout = timeout

    def search_stations(
        self, 
        query: str = "", 
        limit: int = 100, 
        offset: int = 0,
        order_by: str = "clickcount"
    ) -> List[RadioStation]:
        params = {
            "limit": limit,
            "offset": offset,
            "order": order_by,
            "reverse": "true"
        }
        
        if query:
            params["name"] = query

        try:
            response = self.session.get(f"{self.BASE_URL}/stations/search", params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            stations = []
            for item in data:
                station = RadioStation(
                    id=item.get("stationuuid", ""),
                    name=item.get("name", ""),
                    url=item.get("url", ""),
                    bitrate=item.get("bitrate", 0),
                    codec=item.get("codec", ""),
                    country=item.get("country", ""),
                    language=item.get("language", ""),
                    tags=item.get("tags", ""),
                    favicon=item.get("favicon", ""),
                    votes=item.get("votes", 0),
                    click_count=item.get("clickcount", 0)
                )
                stations.append(station)
            
            return stations
        except requests.RequestException:
            return []

    def get_stations_by_country(self, country: str, limit: int = 100) -> List[RadioStation]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/stations/bycountry/{country}",
                params={"limit": limit, "order": "clickcount", "reverse": "true"},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            stations = []
            for item in data:
                station = RadioStation(
                    id=item.get("stationuuid", ""),
                    name=item.get("name", ""),
                    url=item.get("url", ""),
                    bitrate=item.get("bitrate", 0),
                    codec=item.get("codec", ""),
                    country=item.get("country", ""),
                    language=item.get("language", ""),
                    tags=item.get("tags", ""),
                    favicon=item.get("favicon", ""),
                    votes=item.get("votes", 0),
                    click_count=item.get("clickcount", 0)
                )
                stations.append(station)
            
            return stations
        except requests.RequestException:
            return []

    def get_stations_by_tag(self, tag: str, limit: int = 100) -> List[RadioStation]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/stations/bytag/{tag}",
                params={"limit": limit, "order": "clickcount", "reverse": "true"},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            stations = []
            for item in data:
                station = RadioStation(
                    id=item.get("stationuuid", ""),
                    name=item.get("name", ""),
                    url=item.get("url", ""),
                    bitrate=item.get("bitrate", 0),
                    codec=item.get("codec", ""),
                    country=item.get("country", ""),
                    language=item.get("language", ""),
                    tags=item.get("tags", ""),
                    favicon=item.get("favicon", ""),
                    votes=item.get("votes", 0),
                    click_count=item.get("clickcount", 0)
                )
                stations.append(station)
            
            return stations
        except requests.RequestException:
            return []

    def get_popular_stations(self, limit: int = 100) -> List[RadioStation]:
        return self.search_stations(limit=limit, order_by="clickcount")

    def get_station_by_id(self, station_id: str) -> RadioStation:
        """Get a specific station by its ID."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/stations/byuuid/{station_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data:
                item = data[0] if isinstance(data, list) else data
                return RadioStation(
                    id=item.get("stationuuid", ""),
                    name=item.get("name", ""),
                    url=item.get("url", ""),
                    bitrate=item.get("bitrate", 0),
                    codec=item.get("codec", ""),
                    country=item.get("country", ""),
                    language=item.get("language", ""),
                    tags=item.get("tags", ""),
                    favicon=item.get("favicon", ""),
                    votes=item.get("votes", 0),
                    click_count=item.get("clickcount", 0)
                )
            return None
        except requests.RequestException:
            return None

    def is_available(self) -> bool:
        try:
            response = self.session.get(f"{self.BASE_URL}/stations/search", params={"limit": 1}, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False
