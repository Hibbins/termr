from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import DataTable, Footer, Static, Input, OptionList
from textual.binding import Binding
from textual import work
from typing import List, Optional
from textual.theme import Theme

from .models import RadioStation, PlaybackStatus
from .api import RadioBrowserAPI
from .player import VLCPlayer
from .favorites import FavoritesManager
from .config import Config
from .themes import THEMES
from .version import __version__


class StationList(DataTable):
    def __init__(self, stations: List[RadioStation] = None, **kwargs):
        super().__init__(**kwargs)
        self.stations = stations or []
        self.cursor_type = "row"
        self.current_station_id = None
        self.last_cell_info = None

    def on_mount(self) -> None:
        self.add_column("Name", key="Name")
        self.add_column("Country", key="Country")
        self.add_column("Bitrate", key="Bitrate")
        self.add_column("Codec", key="Codec")
        self.load_stations(self.stations)
        if self.row_count > 0:
            self.move_cursor(row=0, column=0)

    def load_stations(self, stations: List[RadioStation]) -> None:
        self.stations = stations
        self.clear()
        for station in stations:
            name = station.name
            if self.id == "favorites-list":
                name = name.replace(" *", "").replace("*", "").strip()
            else:
                if self.app.favorites_manager.is_favorite(station.id):
                    name = name.replace(" *", "").replace("*", "").strip() + " *"
                else:
                    name = name.replace(" *", "").replace("*", "").strip()
            self.add_row(
                name,
                station.country,
                f"{station.bitrate} kbps" if station.bitrate > 0 else "Unknown",
                station.codec.upper() if station.codec else "Unknown",
                key=station.id
            )
        if self.row_count > 0:
            self.move_cursor(row=0, column=0)

    def get_row_key_for_station(self, station_id):
        for key in self._row_locations:
            if hasattr(key, "value") and key.value == station_id:
                return key
        return None

    def update_favorite_indicator(self, station_id: str, is_favorite: bool):
        row_key = self.get_row_key_for_station(station_id)
        column_key = 'Name'
        if row_key is None:
            return
        for station in self.stations:
            if station.id == station_id:
                name = station.name
                if self.id == "station-list":
                    if is_favorite:
                        name = name + " *" if not name.endswith(" *") else name
                self.update_cell(row_key, column_key, name)
                break

    def get_selected_station(self) -> Optional[RadioStation]:
        if self.cursor_row is None:
            return None
        try:
            row_index = self.cursor_row
            if 0 <= row_index < len(self.stations):
                return self.stations[row_index]
        except Exception:
            pass
        return None

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.app.action_play_station()


class SearchInput(Input):
    def __init__(self, **kwargs):
        super().__init__(placeholder="Search for stations...", **kwargs)


class StatusBar(Static):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = PlaybackStatus()
        self.volume = 100
        self.metadata = None
        self.loading_message = None

    def update_status(self, status: PlaybackStatus, volume: int = None, metadata: str = None, loading_message: str = None) -> None:
        self.status = status
        if volume is not None:
            self.volume = volume
        self.metadata = metadata  # Always set, even if None
        self.loading_message = loading_message
        self.refresh()

    def render(self) -> str:
        width = self.size.width if hasattr(self, 'size') and self.size else 80
        if self.loading_message:
            return f"{self.loading_message} | Volume: {self.volume}%".center(width)
        
        if not self.status.station:
            main_line = "No station playing | Volume: {}%".format(self.volume)
            meta_line = "No artist - Unknown title"
            return f"{main_line.center(width)}\n{meta_line.center(width)}"
        
        station = self.status.station
        main_line = f"{station.name} ({station.country}) - {station.bitrate}kbps {station.codec.upper()} | Volume: {self.volume}%"
        if self.metadata and self.metadata.strip() and self.metadata != "-":
            meta_line = self.metadata
        else:
            meta_line = "No artist - Unknown title"
        return f"{main_line.center(width)}\n{meta_line.center(width)}"


class AsciiLogo(Static):
    ASCII = [
        " __                            ",
        "|  |_.-----.----.--------.----.",
        "|   _|  -__|   _|        |   _|",
        "|____|_____|__| |__|__|__|__|  ",
        "                               "
    ]
    def render(self) -> str:
        width = self.size.width if hasattr(self, 'size') and self.size else 80
        art = "\n".join(line.center(width) for line in self.ASCII)
        version = f"Version: {__version__}".center(width)
        return f"{art}\n{version}\n"


class ThemeSelection(OptionList):
    def on_mount(self) -> None:
        self.add_options(list(THEMES.keys()))
        self.highlighted = 0
        self.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        selected_theme = list(THEMES.keys())[event.option_index]
        self.app.apply_theme(selected_theme)
        self.app.refresh()


class HelpScreen(Static):
    can_focus = True
    def render(self) -> str:
        width = self.size.width if hasattr(self, 'size') and self.size else 80
        help_text = """
Help

Arrow keys - Navigates up and down in the menus
Enter - Selects the current option
Escape - Goes back to previous screen

h - Returns to home screen
q - Quits the app
s - Search for stations while in station list
f - Adds the selected station to your favorites list. If the station is already in your favorites list, it will instead be removed
+ / - - Adjusts the volume up or down
"""
        return "\n" + "\n".join(line.center(width) for line in help_text.strip().splitlines())


class HomeScreen(OptionList):
    MENU = [
        "Stations",
        "Favorites",
        "Surprise Me",
        "Themes",
        "Help",
        "Exit"
    ]

    def on_mount(self) -> None:
        self.add_options(self.MENU)
        self.highlighted = 0  # Always highlight the first option on initial load
        self.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        index = event.option_index
        if index == 0:
            self.app.show_station_list()
        elif index == 1:
            self.app.show_favorites_list()
        elif index == 2:
            self.app.action_random_station()
        elif index == 3:
            self.app.show_theme_screen()
        elif index == 4:
            self.app.show_help_screen()
        elif index == 5:
            self.app.exit()


class TermrApp(App):
    CSS_PATH = "termr.css"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("p", "pause_resume", "Pause/Resume"),
        Binding("x", "stop", "Stop"),
        Binding("s", "show_search", "Search"),
        Binding("f", "toggle_favorite", "Add/Remove Favorite"),
        Binding("+", "volume_up", "Vol up"),
        Binding("-", "volume_down", "Vol down"),
        Binding("escape", "go_back", "Back"),
        Binding("h", "show_home", "Home"),
        Binding("r", "refresh_stations", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.config_dir = self.get_config_dir()
        self.config = Config(self.config_dir)
        api_timeout = self.config.get("api_timeout", 10)
        self.api = RadioBrowserAPI(timeout=api_timeout)
        self.player = VLCPlayer()
        self.player.set_app(self)
        self.favorites_manager = FavoritesManager(self.config_dir)
        self.stations: List[RadioStation] = []
        self.favorites: List[RadioStation] = []
        self.current_view = "stations"
        self.station_list: Optional[StationList] = None
        self.favorites_list: Optional[StationList] = None
        self.status_bar: Optional[StatusBar] = None
        self.search_input: Optional[SearchInput] = None
        self.showing_search = False
        self.volume = self.config.get("volume", 100)
        self.metadata: Optional[str] = None
        self._active_theme = self.config.get("theme", "default")

    def get_config_dir(self):
        from pathlib import Path
        return Path.home() / ".config" / "termr"

    def compose(self) -> ComposeResult:
        with Container(id="main"):
            with Vertical():
                yield AsciiLogo(id="ascii-logo")
                with Container(id="home-container"):
                    yield HomeScreen(id="home-screen")
                with Container(id="theme-container", classes="hidden"):
                    pass
                with Container(id="help-container", classes="hidden"):
                    yield HelpScreen(id="help-screen")
                yield SearchInput(id="search-input", classes="hidden")
                yield StationList(id="station-list", classes="hidden")
                yield StationList(id="favorites-list", classes="hidden")
                yield StatusBar(id="status-bar")
            yield Footer()

    def on_mount(self) -> None:
        self.home_container = self.query_one("#home-container")
        self.theme_container = self.query_one("#theme-container")
        self.help_container = self.query_one("#help-container")
        self.home_screen = self.query_one("#home-screen", HomeScreen)
        self.station_list = self.query_one("#station-list", StationList)
        self.favorites_list = self.query_one("#favorites-list", StationList)
        self.status_bar = self.query_one("#status-bar", StatusBar)
        self.search_input = self.query_one("#search-input", SearchInput)
        self.help_screen = self.query_one("#help-screen", HelpScreen)
        self.home_container.remove_class("hidden")
        self.station_list.add_class("hidden")
        self.favorites_list.add_class("hidden")
        self.theme_container.add_class("hidden")
        self.help_container.add_class("hidden")
        self.home_screen.focus()
        self.player.set_volume(self.volume)
        if self.status_bar:
            self.status_bar.update_status(self.player.get_status(), self.volume)
        if self.search_input:
            self.search_input.add_class("hidden")
        self.load_favorites()
        self.current_view = None
        self.apply_theme(self._active_theme)

    def apply_theme(self, theme_name: str) -> None:
        if theme_name in THEMES:
            self._active_theme = theme_name
            self.config.set("theme", theme_name)

            if theme_name == "default":
                self.theme = "textual-dark"
                return
                
            if theme_name not in ("textual-dark", "textual-light", "gruvbox", "tokyo-night", "nord"):
                if theme_name == "light":
                    theme = Theme(
                        name="light",
                        primary="#3498db",
                        secondary="#2c3e50",
                        warning="#e74c3c",
                        error="#e74c3c",
                        success="#27ae60",
                        accent="#e74c3c",
                        foreground="#2c3e50",
                        background="#ecf0f1",
                        surface="#ecf0f1",
                        panel="#bdc3c7",
                        dark=False
                    )
                elif theme_name == "solarized":
                    theme = Theme(
                        name="solarized",
                        primary="#268bd2",
                        secondary="#073642",
                        warning="#cb4b16",
                        error="#dc322f",
                        success="#859900",
                        accent="#d33682",
                        foreground="#839496",
                        background="#002b36",
                        surface="#073642",
                        panel="#073642",
                        dark=True
                    )
                elif theme_name == "monokai":
                    theme = Theme(
                        name="monokai",
                        primary="#f92672",
                        secondary="#75715e",
                        warning="#f92672",
                        error="#f92672",
                        success="#a6e22e",
                        accent="#a6e22e",
                        foreground="#f8f8f2",
                        background="#272822",
                        surface="#3e3d32",
                        panel="#75715e",
                        dark=True
                    )
                elif theme_name == "dracula":
                    theme = Theme(
                        name="dracula",
                        primary="#bd93f9",
                        secondary="#44475a",
                        warning="#ffb86c",
                        error="#ff5555",
                        success="#50fa7b",
                        accent="#ff79c6",
                        foreground="#f8f8f2",
                        background="#282a36",
                        surface="#44475a",
                        panel="#44475a",
                        dark=True
                    )
                else:
                    return
                self.register_theme(theme)
            self.theme = theme_name

    @work(thread=True)
    def load_stations(self, for_favorites: bool = False) -> None:
        """Load stations with retry mechanism and better error handling."""
        max_retries = 3
        retry_delay = 2
        
        def show_loading():
            if self.status_bar and not for_favorites:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message="Loading stations...")
        
        def hide_loading():
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message=None)
        
        def show_error(message: str):
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message=message)
        
        self.call_from_thread(show_loading)
        
        stations = []
        for attempt in range(max_retries):
            try:
                if not self.api.is_available():
                    if attempt == 0:
                        self.call_from_thread(lambda: show_error("API not available, retrying..."))
                    import time
                    time.sleep(retry_delay)
                    continue
                
                max_stations = self.config.get("max_stations", 100)
                sort_by = self.config.get("default_sort", "clickcount")
                stations = self.api.search_stations(limit=max_stations, order_by=sort_by)
                
                if stations:
                    break
                else:
                    if attempt < max_retries - 1:
                        self.call_from_thread(lambda: show_error(f"No stations found, retrying... (attempt {attempt + 1}/{max_retries})"))
                        import time
                        time.sleep(retry_delay)
                    else:
                        self.call_from_thread(lambda: show_error("Failed to load stations after multiple attempts"))
                        return
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    self.call_from_thread(lambda: show_error(f"Error loading stations, retrying... (attempt {attempt + 1}/{max_retries})"))
                    import time
                    time.sleep(retry_delay)
                else:
                    self.call_from_thread(lambda: show_error(f"Failed to load stations: {str(e)}"))
                    return
        
        # Update stations and UI
        self.stations = stations
        
        def update_ui():
            if self.station_list:
                self.station_list.load_stations(stations)
                if self.current_view == "stations" and not self.station_list.has_class("hidden"):
                    self.station_list.focus()
            self.load_favorites()
            
            if stations:
                if not for_favorites:
                    self.update_status(loading_message=f"Loaded {len(stations)} stations")
                    self.call_after_refresh(lambda: self._clear_loading_message_after_delay())
                else:
                    hide_loading()
            else:
                hide_loading()
        
        self.call_from_thread(update_ui)

    @work(thread=True)
    def _clear_loading_message_after_delay(self) -> None:
        import time
        time.sleep(3.0)
        self.call_from_thread(lambda: self.update_status(loading_message=None))

    @work(thread=True)
    def _load_missing_favorites(self, station_ids: List[str]) -> None:
        """Load missing favorite stations from API."""
        if not self.api.is_available():
            return
        
        def show_loading():
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message="Loading missing favorites...")
        
        self.call_from_thread(show_loading)
        
        missing_stations = []
        for station_id in station_ids:
            try:
                station = self.api.get_station_by_id(station_id)
                if station:
                    missing_stations.append(station)
            except Exception:
                continue
        
        def update_ui():
            for station in missing_stations:
                if station.id not in [f.id for f in self.favorites]:
                    self.favorites.append(station)
            
            if self.favorites_list:
                self.favorites_list.load_stations(self.favorites)
            
            if missing_stations:
                self.update_status(loading_message=f"Loaded {len(missing_stations)} missing favorites")
                self.call_after_refresh(lambda: self._clear_loading_message_after_delay())
            else:
                self.update_status(loading_message=None)
        
        self.call_from_thread(update_ui)

    @work(thread=True)
    def search_stations(self, query: str) -> None:
        if not self.api.is_available():
            return
        
        if not query.strip():
            self.load_stations()
            return
        
        def show_loading():
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message=f"Searching for '{query}'...")
        
        self.call_from_thread(show_loading)
        stations = self.api.search_stations(query=query, limit=50)
        
        def update_ui():
            if self.station_list:
                self.station_list.load_stations(stations)
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message=f"Found {len(stations)} stations for '{query}'")
        
        self.call_from_thread(update_ui)

    def load_favorites(self) -> None:
        # Ensure migration is done if needed
        self.favorites_manager.ensure_migration(api=self.api)     

        self.favorites = self.favorites_manager.get_favorites()
        
        if self.favorites_list:
            self.favorites_list.load_stations(self.favorites)

    def action_show_search(self) -> None:
        if self.search_input and not self.showing_search:
            self.search_input.remove_class("hidden")
            self.search_input.focus()
            self.showing_search = True

    def action_hide_search(self) -> None:
        if self.search_input and self.showing_search:
            self.search_input.add_class("hidden")
            self.search_input.value = ""
            self.showing_search = False

            # Restore original station list when search is closed
            if self.current_view == "stations" and self.station_list and self.stations:
                self.station_list.load_stations(self.stations)
            
            current_list = self.favorites_list if self.current_view == "favorites" else self.station_list
            if current_list:
                current_list.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input == self.search_input:
            query = event.value
            if query.strip():
                self.search_stations(query)
            else:
                self.action_hide_search()
            current_list = self.favorites_list if self.current_view == "favorites" else self.station_list
            if current_list:
                current_list.focus()

    def action_play_station(self) -> None:
        current_list = self.favorites_list if self.current_view == "favorites" else self.station_list
        if not current_list:
            current_list = self.station_list or self.favorites_list
        if not current_list:
            return
        station = current_list.get_selected_station()
        if station:
            if not station.url:
                self.notify(f"The station '{station.name}' does not have a valid URL and cannot be played.", severity="error")
                return
            self.metadata = None
            self.update_status()
            result = self.player.play(station, self.volume)
            if not result:
                self.notify(f"Could not start playback of '{station.name}'. Please check if the stream is available.", severity="error")
            self.config.set("last_station", station.id)

    def action_pause_resume(self) -> None:
        if self.player.toggle_pause():
            self.update_status(loading_message=None)

    def action_stop(self) -> None:
        self.player.stop()
        self.metadata = None
        self.update_status()

    def action_toggle_favorite(self) -> None:
        current_list = self.favorites_list if self.current_view == "favorites" else self.station_list
        if not current_list:
            current_list = self.station_list or self.favorites_list
        if not current_list:
            return
        station = current_list.get_selected_station()
        if not station:
            return
        if self.favorites_manager.is_favorite(station.id):
            self.favorites_manager.remove_favorite(station.id)
            message = f"Removed {station.name} from favorites"
        else:
            self.favorites_manager.add_favorite(station)
            message = f"Added {station.name} to favorites"
        self.load_favorites()
        current_list.update_favorite_indicator(station.id, self.favorites_manager.is_favorite(station.id))
        self.update_status(loading_message=message)

    def action_random_station(self) -> None:
        import random
        available_stations = self.favorites if self.current_view == "favorites" else self.stations
        if not available_stations:
            available_stations = self.stations or self.favorites
        if available_stations:
            station = random.choice(available_stations)
            self.metadata = None
            self.update_status()
            self.player.play(station)
            self.config.set("last_station", station.id)
            if self.current_view == "favorites":
                lst = self.favorites_list
            else:
                lst = self.station_list
            if lst:
                for idx, s in enumerate(lst.stations):
                    if s.id == station.id:
                        lst.move_cursor(row=idx, column=0)
                        break

    def action_switch_view(self) -> None:
        if self.current_view == "stations":
            self.current_view = "favorites"
            self.station_list.add_class("hidden")
            self.favorites_list.remove_class("hidden")
            self.favorites_list.focus()
        else:
            self.current_view = "stations"
            self.favorites_list.add_class("hidden")
            self.station_list.remove_class("hidden")
            self.station_list.focus()

    def update_status(self, loading_message: str = None) -> None:
        if self.status_bar:
            status = self.player.get_status()
            self.status_bar.update_status(status, self.volume, metadata=self.metadata, loading_message=loading_message)

    def on_key(self, event) -> None:
        if event.key in ("h", "escape") and self.current_view in ("theme", "help"):
            self.action_show_home()
        self.update_status()

    def on_unmount(self) -> None:
        self.player.stop()

    def action_volume_up(self) -> None:
        if self.volume < 200:
            self.volume = min(200, self.volume + 5)
            self.config.set("volume", self.volume)
            self.player.set_volume(self.volume)
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message=None)

    def action_volume_down(self) -> None:
        if self.volume > 0:
            self.volume = max(0, self.volume - 5)
            self.config.set("volume", self.volume)
            self.player.set_volume(self.volume)
            if self.status_bar:
                self.status_bar.update_status(self.player.get_status(), self.volume, loading_message=None)

    def set_metadata(self, meta: str, station_id: str = None) -> None:
        current_station = self.player.get_current_station()
        if not current_station or (station_id is not None and station_id != current_station.id):
            return
        parts = meta.split("-", 1) if meta else []
        if (
            not meta
            or not meta.strip()
            or meta == "-"
            or len(parts) != 2
            or not parts[0].strip()
            or not parts[1].strip()
        ):
            self.metadata = None
        else:
            self.metadata = meta
        self.update_status()

    def show_station_list(self):
        self.home_container.add_class("hidden")
        self.station_list.remove_class("hidden")
        self.station_list.focus()
        self.current_view = "stations"
        
        if not self.stations:
            self.load_stations()
        elif self.station_list and not self.station_list.stations:
            # If stations are loaded but station_list is empty, reload it
            self.station_list.load_stations(self.stations)

    def show_favorites_list(self):
        self.home_container.add_class("hidden")
        self.favorites_list.remove_class("hidden")
        self.favorites_list.focus()
        self.current_view = "favorites"
        
        # Load stations if not already loaded (needed for favorites)
        if not self.stations:
            self.load_stations(for_favorites=True)

    def action_show_home(self):
        self.home_container.remove_class("hidden")
        self.theme_container.add_class("hidden")
        self.help_container.add_class("hidden")
        self.station_list.add_class("hidden")
        self.favorites_list.add_class("hidden")
        self.home_screen.focus()
        self.current_view = None

    def show_theme_screen(self):
        self.home_container.add_class("hidden")
        self.theme_container.remove_class("hidden")

        for widget in list(self.theme_container.children):
            if isinstance(widget, ThemeSelection):
                widget.remove()

        theme_selection = ThemeSelection()
        self.theme_container.mount(theme_selection)
        theme_selection.focus()
        self.current_view = "theme"

    def show_help_screen(self):
        self.home_container.add_class("hidden")
        self.theme_container.add_class("hidden")
        self.help_container.remove_class("hidden")
        self.station_list.add_class("hidden")
        self.favorites_list.add_class("hidden")
        self.help_screen.focus()
        self.current_view = "help"

    def action_refresh_stations(self) -> None:
        """Refresh the stations list."""
        if self.current_view == "stations":
            self.update_status(loading_message="Refreshing stations...")
            self.load_stations()

    def action_go_back(self) -> None:
        if self.current_view in ("theme", "help"):
            self.action_show_home()
        elif self.showing_search:
            self.action_hide_search()
        elif self.current_view in ("stations", "favorites"):
            self.action_show_home()
        else:
            self.action_show_home()
