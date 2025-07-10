from pathlib import Path

THEMES = {
    "default": """
* {
    background: #23243a;
}
Screen, #main, Vertical {
    background: #23243a;
    height: 1fr;
    width: 1fr;
    margin: 0;
    padding: 0;
}
#ascii-logo {
    background: #23243a;
    color: #e0e0e0;
    width: 100%;
    height: auto;
    min-height: 5;
    margin: 0;
    padding: 0;
    align: center middle;
    content-align: center middle;
}
/* Default theme - Dark with blue accents */
#main {
    layout: vertical;
}

#search-input {
    height: 3;
    margin: 1;
    border: solid #3949ab;
}

#search-input.hidden {
    display: none;
}

#station-list, #favorites-list {
    height: 1fr;
    border: heavy #3949ab;
}

#station-list.hidden {
    display: none;
}

#favorites-list.hidden {
    display: none;
}

#status-bar {
    height: 8;
    color: #e0e0e0;
    align: center middle;
    content-align: center middle;
    border: heavy #3949ab;
}

DataTable {
    background: transparent;
    color: #e0e0e0;
}

DataTable > .datatable--header {
    background: #3949ab;
    color: #e0e0e0;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #82aaff;
    color: #23243a;
}

DataTable > .datatable--row {
    background: transparent;
    color: #e0e0e0;
}

DataTable > .datatable--row:hover {
    background: #1a1a2e;
}

Header {
    background: #3949ab;
    color: #e0e0e0;
    text-style: bold;
}

Footer {
    background: #3949ab;
    color: #e0e0e0;
}

#home-container.hidden {
    display: none;
}

#home-container {
    height: 1fr;
}

MenuHeader {
    height: auto;
}
""",

    "light": """
* {
    background: #ecf0f1;
}
Screen, #main, Vertical {
    background: #ecf0f1;
    height: 1fr;
    width: 1fr;
    margin: 0;
    padding: 0;
}
#ascii-logo {
    background: #ecf0f1;
    color: #2c3e50;
    width: 100%;
    height: auto;
    min-height: 5;
    margin: 0;
    padding: 0;
    align: center middle;
    content-align: center middle;
}
/* Light theme - Light background with dark text */
#main {
    layout: vertical;
}

#search-input {
    height: 3;
    margin: 1;
    border: solid #2c3e50;
    background: #ecf0f1;
    color: #2c3e50;
}

#search-input.hidden {
    display: none;
}

#station-list, #favorites-list {
    height: 1fr;
    border: heavy #2c3e50;
    background: #ecf0f1;
    color: #2c3e50;
}

#station-list.hidden {
    display: none;
}

#favorites-list.hidden {
    display: none;
}

#status-bar {
    height: 8;
    color: #2c3e50;
    align: center middle;
    content-align: center middle;
    border: heavy #2c3e50;
    background: #ecf0f1;
}

DataTable {
    background: transparent;
    color: #2c3e50;
}

DataTable > .datatable--header {
    background: #3498db;
    color: white;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #e74c3c;
    color: white;
}

DataTable > .datatable--row {
    background: transparent;
    color: #2c3e50;
}

DataTable > .datatable--row:hover {
    background: #bdc3c7;
}

Header {
    background: #3498db;
    color: white;
    text-style: bold;
}

Footer {
    background: #3498db;
    color: white;
}

#home-container.hidden {
    display: none;
}

#home-container {
    height: 1fr;
    background: #ecf0f1;
    color: #2c3e50;
}

MenuHeader {
    height: auto;
}
""",

    "solarized": """
* {
    background: #002b36;
}
Screen, #main, Vertical {
    background: #002b36;
    height: 1fr;
    width: 1fr;
    margin: 0;
    padding: 0;
}
#ascii-logo {
    background: #002b36;
    color: #839496;
    width: 100%;
    height: auto;
    min-height: 5;
    margin: 0;
    padding: 0;
    align: center middle;
    content-align: center middle;
}
/* Solarized Dark theme */
#main {
    layout: vertical;
}

#search-input {
    height: 3;
    margin: 1;
    border: solid #268bd2;
    background: #002b36;
    color: #839496;
}

#search-input.hidden {
    display: none;
}

#station-list, #favorites-list {
    height: 1fr;
    border: heavy #268bd2;
    background: #002b36;
    color: #839496;
}

#station-list.hidden {
    display: none;
}

#favorites-list.hidden {
    display: none;
}

#status-bar {
    height: 8;
    color: #839496;
    align: center middle;
    content-align: center middle;
    border: heavy #268bd2;
    background: #002b36;
}

DataTable {
    background: transparent;
    color: #839496;
}

DataTable > .datatable--header {
    background: #073642;
    color: #93a1a1;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #d33682;
    color: #fdf6e3;
}

DataTable > .datatable--row {
    background: transparent;
    color: #839496;
}

DataTable > .datatable--row:hover {
    background: #073642;
}

Header {
    background: #073642;
    color: #93a1a1;
    text-style: bold;
}

Footer {
    background: #073642;
    color: #93a1a1;
}

#home-container.hidden {
    display: none;
}

#home-container {
    height: 1fr;
    background: #002b36;
    color: #839496;
}

MenuHeader {
    height: auto;
}
""",

    "monokai": """
* {
    background: #272822;
}
Screen, #main, Vertical {
    background: #272822;
    height: 1fr;
    width: 1fr;
    margin: 0;
    padding: 0;
}
#ascii-logo {
    background: #272822;
    color: #f8f8f2;
    width: 100%;
    height: auto;
    min-height: 5;
    margin: 0;
    padding: 0;
    align: center middle;
    content-align: center middle;
}
/* Monokai theme - Dark with bright colors */
#main {
    layout: vertical;
}

#search-input {
    height: 3;
    margin: 1;
    border: solid #f92672;
    background: #272822;
    color: #f8f8f2;
}

#search-input.hidden {
    display: none;
}

#station-list, #favorites-list {
    height: 1fr;
    border: heavy #f92672;
    background: #272822;
    color: #f8f8f2;
}

#station-list.hidden {
    display: none;
}

#favorites-list.hidden {
    display: none;
}

#status-bar {
    height: 8;
    color: #f8f8f2;
    align: center middle;
    content-align: center middle;
    border: heavy #f92672;
    background: #272822;
}

DataTable {
    background: transparent;
    color: #f8f8f2;
}

DataTable > .datatable--header {
    background: #75715e;
    color: #f8f8f2;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #a6e22e;
    color: #272822;
}

DataTable > .datatable--row {
    background: transparent;
    color: #f8f8f2;
}

DataTable > .datatable--row:hover {
    background: #3e3d32;
}

Header {
    background: #75715e;
    color: #f8f8f2;
    text-style: bold;
}

Footer {
    background: #75715e;
    color: #f8f8f2;
}

#home-container.hidden {
    display: none;
}

#home-container {
    height: 1fr;
    background: #272822;
    color: #f8f8f2;
}

MenuHeader {
    height: auto;
}
""",

    "dracula": """
* {
    background: #282a36;
}
Screen, #main, Vertical {
    background: #282a36;
    height: 1fr;
    width: 1fr;
    margin: 0;
    padding: 0;
}
#ascii-logo {
    background: #282a36;
    color: #f8f8f2;
    width: 100%;
    height: auto;
    min-height: 5;
    margin: 0;
    padding: 0;
    align: center middle;
    content-align: center middle;
}
/* Dracula theme - Dark purple */
#main {
    layout: vertical;
}

#search-input {
    height: 3;
    margin: 1;
    border: solid #bd93f9;
    background: #282a36;
    color: #f8f8f2;
}

#search-input.hidden {
    display: none;
}

#station-list, #favorites-list {
    height: 1fr;
    border: heavy #bd93f9;
    background: #282a36;
    color: #f8f8f2;
}

#station-list.hidden {
    display: none;
}

#favorites-list.hidden {
    display: none;
}

#status-bar {
    height: 8;
    color: #f8f8f2;
    align: center middle;
    content-align: center middle;
    border: heavy #bd93f9;
    background: #282a36;
}

DataTable {
    background: transparent;
    color: #f8f8f2;
}

DataTable > .datatable--header {
    background: #44475a;
    color: #f8f8f2;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #ff79c6;
    color: #282a36;
}

DataTable > .datatable--row {
    background: transparent;
    color: #f8f8f2;
}

DataTable > .datatable--row:hover {
    background: #44475a;
}

Header {
    background: #44475a;
    color: #f8f8f2;
    text-style: bold;
}

Footer {
    background: #44475a;
    color: #f8f8f2;
}

#home-container.hidden {
    display: none;
}

#home-container {
    height: 1fr;
    background: #282a36;
    color: #f8f8f2;
}

MenuHeader {
    height: auto;
}
""",
}

def get_theme_css_path(theme_name: str) -> str:
    """Get the path to the CSS file for a theme."""
    themes_dir = Path(__file__).parent / "themes"
    themes_dir.mkdir(exist_ok=True)
    
    # Base CSS file
    base_css = themes_dir / "termr.css"
    
    # Theme-specific CSS file
    if theme_name in THEMES:
        css_file = themes_dir / f"{theme_name}.css"
        
        if not css_file.exists():
            with open(css_file, 'w') as f:
                f.write(THEMES[theme_name])
        
        return str(css_file)
    else:
        return str(base_css)
