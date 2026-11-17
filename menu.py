"""Reads the week's lunch menu and prepares it for the page."""

import json
from pathlib import Path

MENU_FILE = Path(__file__).parent / "menu.json"

WEEKDAYS = ("mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag")


def load_menu(path: Path = MENU_FILE) -> dict:
    """Return the menu as stored in the JSON file."""
    with path.open(encoding="utf-8") as menu_file:
        return json.load(menu_file)


def days_in_order(menu: dict) -> list[str]:
    """Return the days that have a menu: weekdays in week order, then other names alphabetically."""

    def position(day: str) -> tuple[int, str]:
        rank = WEEKDAYS.index(day) if day in WEEKDAYS else len(WEEKDAYS)
        return (rank, day)

    return sorted(menu["days"], key=position)


def week_view(menu: dict) -> list[dict]:
    """Return one entry per day with the day's dishes, ready for the template."""
    return [{"day": day, "dishes": menu["days"][day]} for day in days_in_order(menu)]
