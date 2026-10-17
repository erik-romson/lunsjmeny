"""Reads the week's lunch menu and prepares it for the page."""

import json
from datetime import date
from pathlib import Path

MENU_FILE = Path(__file__).parent / "menu.json"
WEEKDAY_NAMES = ("mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag")


def load_menu(path: Path = MENU_FILE) -> dict:
    """Return the menu as stored in the JSON file."""
    with path.open(encoding="utf-8") as menu_file:
        return json.load(menu_file)


def days_in_order(menu: dict) -> list[str]:
    """Return the days that have a menu, in weekday order."""
    return sorted(menu["days"], key=WEEKDAY_NAMES.index)


def menu_day_for(menu: dict, day: date) -> str | None:
    """Return the menu day that falls on `day`, or None when that day has no menu."""
    if day.isocalendar().week != menu["week"]:
        return None
    name = WEEKDAY_NAMES[day.weekday()]
    return name if name in menu["days"] else None


def week_view(menu: dict, today: date) -> list[dict]:
    """Return one entry per day with the day's dishes and whether it is `today`
    (`is_today`), ready for the template."""
    today_day = menu_day_for(menu, today)
    return [
        {"day": day, "dishes": menu["days"][day], "is_today": day == today_day}
        for day in days_in_order(menu)
    ]
