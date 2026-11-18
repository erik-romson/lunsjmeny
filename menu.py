"""Reads the week's lunch menu and prepares it for the page."""

import json
from collections.abc import Iterable
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


def normalize_allergen(name: str) -> str:
    """Return the allergen name trimmed and case-folded, for comparing."""
    return name.strip().casefold()


def chosen_allergens(values: Iterable[str]) -> list[str]:
    """Return the chosen allergen names normalised, without blanks or repeats, sorted."""
    names = {normalize_allergen(value) for value in values}
    names.discard("")
    return sorted(names)


def allergens_in_week(menu: dict) -> list[str]:
    """Return every allergen used by this week's dishes, once each, sorted."""
    names = {
        normalize_allergen(allergen)
        for dishes in menu["days"].values()
        for dish in dishes
        for allergen in dish["allergens"]
    }
    names.discard("")
    return sorted(names)


def hide_dishes(days: list[dict], chosen: Iterable[str]) -> list[dict]:
    """Return the days without the dishes that contain a chosen allergen."""
    hidden = set(chosen_allergens(chosen))
    result = []
    for entry in days:
        kept = [
            dish
            for dish in entry["dishes"]
            if hidden.isdisjoint(normalize_allergen(a) for a in dish["allergens"])
        ]
        result.append({**entry, "dishes": kept})
    return result
