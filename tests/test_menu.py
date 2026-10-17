from datetime import date

import pytest

from menu import load_menu, menu_day_for, week_view

MENU = {"week": 43, "days": {
    "mandag": [{"name": "Fiskesuppe", "price": 95, "allergens": []}],
    "tirsdag": [{"name": "Kyllingtaco", "price": 99, "allergens": []}],
    "fredag": [{"name": "Pizza", "price": 98, "allergens": []}],
}}


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 43, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu, date(2026, 10, 19))

    assert view == [
        {"day": "mandag", "dishes": [{"name": "Suppe", "price": 80, "allergens": []}], "is_today": True}
    ]


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2026, 10, 19), "mandag"),
        (date(2026, 10, 20), "tirsdag"),
        (date(2026, 10, 23), "fredag"),
        (date(2026, 10, 21), None),
        (date(2026, 10, 24), None),
        (date(2026, 10, 25), None),
        (date(2026, 10, 13), None),
    ],
)
def test_menu_day_for(day, expected):
    assert menu_day_for(MENU, day) == expected


def test_week_view_marks_only_today():
    view = week_view(MENU, date(2026, 10, 20))

    assert {e["day"]: e["is_today"] for e in view} == {"mandag": False, "tirsdag": True, "fredag": False}
    assert all(e["dishes"] == MENU["days"][e["day"]] for e in view)
