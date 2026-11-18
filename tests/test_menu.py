from datetime import date

import pytest

from menu import day_name, load_menu, week_view

FIVE_DAY_MENU = {
    "week": 43,
    "days": {
        "mandag": [{"name": "Fiskesuppe", "price": 80, "allergens": []}],
        "tirsdag": [{"name": "Taco", "price": 85, "allergens": []}],
        "onsdag": [{"name": "Kjøttkaker", "price": 90, "allergens": []}],
        "torsdag": [{"name": "Ertesuppe", "price": 80, "allergens": []}],
        "fredag": [{"name": "Pizza", "price": 95, "allergens": []}],
    },
}


def by_day(view):
    return {entry["day"]: entry for entry in view}


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 1, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu, date(2026, 10, 20))

    assert view == [
        {
            "day": "mandag",
            "dishes": [{"name": "Suppe", "price": 80, "allergens": []}],
            "is_today": False,
        }
    ]


@pytest.mark.parametrize(
    ("on", "expected"),
    [
        (date(2026, 10, 19), "mandag"),
        (date(2026, 10, 20), "tirsdag"),
        (date(2026, 10, 21), "onsdag"),
        (date(2026, 10, 22), "torsdag"),
        (date(2026, 10, 23), "fredag"),
        (date(2026, 10, 24), "lørdag"),
        (date(2026, 10, 25), "søndag"),
    ],
)
def test_day_name_is_the_bokmal_weekday(on, expected):
    assert day_name(on) == expected


def test_week_view_marks_only_the_weekday_of_the_date_as_today():
    view = week_view(FIVE_DAY_MENU, date(2026, 10, 21))

    entries = by_day(view)
    assert {entry["day"] for entry in view} == set(FIVE_DAY_MENU["days"])
    assert [day for day, entry in entries.items() if entry["is_today"]] == ["onsdag"]
    for day, entry in entries.items():
        assert entry["dishes"] == FIVE_DAY_MENU["days"][day]


def test_week_view_marks_nothing_on_a_saturday():
    view = week_view(FIVE_DAY_MENU, date(2026, 10, 24))

    entries = by_day(view)
    assert set(entries) == set(FIVE_DAY_MENU["days"])
    assert not any(entry["is_today"] for entry in view)
    for day, entry in entries.items():
        assert entry["dishes"] == FIVE_DAY_MENU["days"][day]


def test_week_view_marks_nothing_on_a_sunday():
    view = week_view(FIVE_DAY_MENU, date(2026, 10, 25))

    assert not any(entry["is_today"] for entry in view)


def test_week_view_marks_nothing_when_the_menu_lacks_todays_day():
    menu = {"week": 43, "days": {"mandag": [], "fredag": []}}

    view = week_view(menu, date(2026, 10, 21))

    assert not any(entry["is_today"] for entry in view)


def test_week_view_marks_nothing_in_another_week():
    # The menu is for week 43; 2026-11-18 is a Wednesday in ISO week 47.
    view = week_view(FIVE_DAY_MENU, date(2026, 11, 18))

    assert not any(entry["is_today"] for entry in view)


def test_week_view_highlights_a_weekend_day_the_menu_has():
    menu = {"week": 43, "days": {"fredag": [], "lørdag": []}}

    entries = by_day(week_view(menu, date(2026, 10, 24)))

    assert entries["lørdag"]["is_today"] is True
    assert entries["fredag"]["is_today"] is False
