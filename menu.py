"""Reads the week's lunch menu and prepares it for the page."""

import json
from datetime import date
from pathlib import Path

MENU_FILE = Path(__file__).parent / "menu.json"

# Indexed by date.weekday(): Monday = 0, Sunday = 6.
WEEKDAY_NAMES = ("mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag")


def load_menu(path: Path = MENU_FILE) -> dict:
    """Return the menu as stored in the JSON file."""
    with path.open(encoding="utf-8") as menu_file:
        return json.load(menu_file)


def days_in_order(menu: dict) -> list[str]:
    """Return the days that have a menu, in a stable order."""
    return sorted(menu["days"])


def day_name(on: date) -> str:
    """Return the lowercase bokmål weekday name of the given date."""
    return WEEKDAY_NAMES[on.weekday()]


def week_view(menu: dict, today: date) -> list[dict]:
    """Return one entry per day with the day's dishes, ready for the template.

    Each entry also says whether it is today's day. A day is today only when
    the menu's week number is the ISO week of `today`.
    """
    this_week = menu["week"] == today.isocalendar().week
    return [
        {"day": day, "dishes": menu["days"][day], "is_today": this_week and day == day_name(today)}
        for day in days_in_order(menu)
    ]
