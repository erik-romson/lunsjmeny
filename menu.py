"""Reads the week's lunch menu and prepares it for the page."""

import json
from pathlib import Path

MENU_FILE = Path(__file__).parent / "menu.json"


def load_menu(path: Path = MENU_FILE) -> dict:
    """Return the menu as stored in the JSON file."""
    with path.open(encoding="utf-8") as menu_file:
        return json.load(menu_file)


def days_in_order(menu: dict) -> list[str]:
    """Return the days that have a menu, in a stable order."""
    return sorted(menu["days"])


def week_view(menu: dict) -> list[dict]:
    """Return one entry per day with the day's dishes, ready for the template."""
    return [{"day": day, "dishes": menu["days"][day]} for day in days_in_order(menu)]
