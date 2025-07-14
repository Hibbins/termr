<div align="center">
  <img src="https://github.com/Hibbins/termr/raw/main/assets/termr_github_banner.png" />
  <br />
  <h1 align="center">termr</h1>
  <p align="center">A simple, fast, and modern terminal radio player.</p>
  <p>
    <a href="https://github.com/Hibbins/termr/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Hibbins/termr.svg" alt="GitHub Stars"/></a>
    <a href="https://github.com/Hibbins/termr/forks" target="_blank"><img src="https://img.shields.io/github/forks/Hibbins/termr.svg" alt="GitHub Forks"/></a>
    <a href="https://github.com/Hibbins/termr/releases" target="_blank"><img src="https://img.shields.io/github/release/Hibbins/termr.svg" alt="Releases"/></a>
    <a href="https://aur.archlinux.org/packages/termr" target="_blank"><img src="https://img.shields.io/aur/version/termr" alt="AUR Version"/></a>
    <a href="https://github.com/Hibbins/termr/issues" target="_blank"><img src="https://img.shields.io/github/issues/Hibbins/termr.svg" alt="GitHub Issues"/></a>
    <a href="https://github.com/Hibbins/termr/releases" target="_blank"><img src="https://img.shields.io/github/downloads/Hibbins/termr/total.svg" alt="Package Downloads"/></a>
    <a href="https://github.com/Hibbins/termr/blob/master/LICENSE" target="_blank"><img src="https://img.shields.io/github/license/Hibbins/termr.svg" alt="License"/></a>
  </p>
</div>
<br />
<div align="center">
  <a href="https://ko-fi.com/M4M615Y5RB" target="_blank"><img width="200" src="https://github.com/user-attachments/assets/91dc5e85-3b94-4424-920c-497b32fc30a4" alt='Buy Me a Coffee at ko-fi.com' /></a>
</div>

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Linux](#linux)
    - [Arch Linux (AUR)](#arch-linux-aur)
    - [Ubuntu/Debian](#ubuntudebian)
    - [From PyPI](#from-pypi)
    - [From Source (Universal)](#from-source-universal)
    - [Requirements](#requirements)
- [Usage Guide](#usage-guide)
  - [Main Functions](#main-functions)
    - [Browse Stations](#browse-stations)
    - [Search](#search)
    - [Favorites](#favorites)
    - [Themes](#themes)
    - [Keyboard Shortcuts](#keyboard-shortcuts)
- [Configuration](#configuration)
  - [Settings](#settings)
  - [Options](#options)
    - [Volume](#volume)
    - [Theme](#theme)
    - [Max Stations](#max-stations)
    - [Default Sort](#default-sort)
    - [API Timeout](#api-timeout)
    - [Autoplay](#autoplay)
- [Troubleshooting](#troubleshooting)

## Features

- Fast, modern TUI radio player built with [Textual](https://github.com/Textualize/textual)
- Browse, search, and play thousands of internet radio stations
- Add and manage favorites
- Multiple color themes
- Volume control, pause/resume, and stop
- Minimal dependencies, easy to install
- Configurable and hackable

## Installation

### Linux

#### Arch Linux (AUR)

```bash
# With pacman
sudo pacman -S termr

# With yay
yay -S termr

# Or clone and build manually
git clone https://aur.archlinux.org/termr.git
cd termr
makepkg -si
```

#### Ubuntu/Debian

```bash
# Download and install
wget https://github.com/Hibbins/termr/releases/download/v1.2.0/termr_1.2.0-1_all.deb
sudo apt install ./termr_1.2.0-1_all.deb
```

#### From PyPI

```bash
pip install termr
```

#### From Source (Universal)

```bash
# Clone and install from source
git clone https://github.com/Hibbins/termr.git
cd termr
pip install .

# Or install directly from GitHub
pip install git+https://github.com/Hibbins/termr.git
```

#### Requirements
- VLC Media Player (with cvlc command)

## Usage Guide

### Main Functions

#### Browse Stations
Navigate the main list to discover and play radio stations from around the world.

#### Search
Press `s` to search for stations by name, genre, country, etc.

#### Favorites
Press `f` to add/remove the selected station to/from your favorites. Access your favorites from the main menu.

#### Themes
Switch between multiple color themes from the menu for the best TUI experience.

#### Keyboard Shortcuts

| Key         | Action                       |
|-------------|------------------------------|
| `q`         | Quit                         |
| `h`         | Home                         |
| `s`         | Search                       |
| `f`         | Add/Remove Favorite          |
| `+` / `-`   | Volume Up/Down               |
| `p`         | Pause/Resume                 |
| `x`         | Stop                         |
| `r`         | Refresh station list         |
| `escape`    | Back                         |
| `enter`     | Play selected station        |

## Configuration

The application automatically creates configuration files in `~/.config/termr/`:

- `favorites.json` - Favorite stations
- `settings.json` - Application settings

### Settings

You can edit `~/.config/termr/settings.json`:

```json
{
  "max_stations": 100,
  "default_sort": "clickcount",
  "auto_play": false,
  "volume": 100,
  "theme": "default",
  "last_station": null,
  "api_timeout": 10
}
```

### Options

#### Volume
Default playback volume (0-200).

#### Theme
Choose your preferred color theme.

#### Max Stations
Set the maximum number of stations to load.

#### Default Sort
Choose how stations are sorted (e.g., by popularity).

#### API Timeout
Set the timeout for API requests.

#### Autoplay
If enabled, termr will automatically start playing the last played station on launch.

## Troubleshooting

### "VLC not found"
Install VLC according to the instructions above.

### "Package not found"
Check that you are using the correct package manager for your system.

### "Permission denied"
```bash
chmod +x termr
```

---

Enjoy listening!  
If you like the project, consider starring it on GitHub or buying me a coffee!

---
