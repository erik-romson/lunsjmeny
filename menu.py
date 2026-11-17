"""Reads the week's lunch menu and prepares it for the page."""

import json
import unicodedata
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


def normalize_allergen(label: str) -> str:
    """Return the label in NFC, stripped and casefolded."""
    return unicodedata.normalize("NFC", label).strip().casefold()


def excluded_allergens(values: Iterable[str]) -> frozenset[str]:
    """Return the normalised selection, without values that are empty."""
    normalized = (normalize_allergen(value) for value in values)
    return frozenset(value for value in normalized if value)


def dish_allergens(dish: dict) -> list[str] | None:
    """Return the dish's normalised allergens, or None when they are not stated."""
    allergens = dish.get("allergens")
    if not isinstance(allergens, list) or not all(isinstance(item, str) for item in allergens):
        return None
    labels = (normalize_allergen(item) for item in allergens)
    return list(dict.fromkeys(label for label in labels if label))


def is_hidden(dish: dict, excluded: frozenset[str]) -> bool:
    """Return True when the dish must be hidden for the selected allergens."""
    if not excluded:
        return False
    allergens = dish_allergens(dish)
    return allergens is None or not excluded.isdisjoint(allergens)


def week_view(menu: dict, excluded: frozenset[str] = frozenset()) -> list[dict]:
    """Return one entry per day with its visible dishes, ready for the template."""
    view = []
    for day in days_in_order(menu):
        day_dishes = menu["days"][day]
        kept = [
            {**dish, "allergens": dish_allergens(dish)}
            for dish in day_dishes
            if not is_hidden(dish, excluded)
        ]
        view.append({"day": day, "dishes": kept, "all_hidden": bool(day_dishes) and not kept})
    return view


def week_allergens(menu: dict) -> list[str]:
    """Return the sorted allergen labels used anywhere in the week."""
    labels: set[str] = set()
    for day in days_in_order(menu):
        for dish in menu["days"][day]:
            labels.update(dish_allergens(dish) or [])
    return sorted(labels)


def allergen_choices(menu: dict, excluded: frozenset[str]) -> list[str]:
    """Return the week's allergens plus the selected ones, sorted."""
    return sorted(set(week_allergens(menu)) | excluded)


def unmatched_allergens(menu: dict, excluded: frozenset[str]) -> list[str]:
    """Return the selected values that match no allergen of the week."""
    return sorted(excluded - set(week_allergens(menu)))
