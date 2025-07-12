#!/usr/bin/env python3
"""Main entry point for termr application."""

import sys
import argparse
from .ui import TermrApp
from .version import __version__


def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    try:
        import subprocess
        result = subprocess.run(
            ["cvlc", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode != 0:
            print("Error: VLC (cvlc) is not available. Please install VLC.")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Error: VLC (cvlc) is not installed. Please install VLC.")
        return False
    
    return True


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Terminal-based radio player with TUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  termr                    Start the application
  termr --help            Show this help message
  termr --version         Show version information

Controls:
  ↑/↓                     Navigate through stations
  Enter                   Play selected station
  p                       Pause/resume playback
  s                       Stop playback
  f                       Add/remove favorite
  r                       Play random station
  Tab                     Switch between views
  q                       Quit application
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"termr {__version__}"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    if not check_dependencies():
        return 1
    
    try:
        app = TermrApp()
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
