from datetime import date

import pytest

from menu import day_name, load_menu, week_view

FIVE_DAY_MENU = {
    "week": 43,
    "days": {
        "mandag": [{"name": "Fiskesuppe", "price": 95, "allergens": ["fisk"]}],
        "tirsdag": [{"name": "Kjøttkaker", "price": 120, "allergens": ["gluten"]}],
        "onsdag": [{"name": "Vegetargryte", "price": 105, "allergens": []}],
        "torsdag": [{"name": "Lasagne", "price": 110, "allergens": ["gluten", "melk"]}],
        "fredag": [{"name": "Taco", "price": 100, "allergens": ["melk"]}],
    },
}


def by_day(view: list[dict]) -> dict[str, dict]:
    return {entry["day"]: entry for entry in view}


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 1, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu, date(2026, 11, 16))

    assert view == [
        {
            "day": "mandag",
            "dishes": [{"name": "Suppe", "price": 80, "allergens": []}],
            "is_today": True,
        }
    ]


@pytest.mark.parametrize(
    ("on", "expected"),
    [
        (date(2026, 11, 16), "mandag"),
        (date(2026, 11, 17), "tirsdag"),
        (date(2026, 11, 18), "onsdag"),
        (date(2026, 11, 19), "torsdag"),
        (date(2026, 11, 20), "fredag"),
        (date(2026, 11, 21), "lørdag"),
        (date(2026, 11, 22), "søndag"),
    ],
)
def test_day_name_gives_the_bokmal_weekday(on, expected):
    assert day_name(on) == expected


def test_week_view_marks_only_wednesday_on_a_wednesday():
    view = week_view(FIVE_DAY_MENU, date(2026, 11, 18))

    assert [entry["day"] for entry in view if entry["is_today"]] == ["onsdag"]
    for entry in view:
        assert entry["dishes"] == FIVE_DAY_MENU["days"][entry["day"]]


def test_week_view_marks_no_day_on_a_saturday():
    view = week_view(FIVE_DAY_MENU, date(2026, 11, 21))

    assert not any(entry["is_today"] for entry in view)
    assert set(by_day(view)) == set(FIVE_DAY_MENU["days"])
    for entry in view:
        assert entry["dishes"] == FIVE_DAY_MENU["days"][entry["day"]]


def test_week_view_marks_no_day_on_a_sunday():
    view = week_view(FIVE_DAY_MENU, date(2026, 11, 22))

    assert not any(entry["is_today"] for entry in view)


def test_week_view_marks_nothing_when_today_is_not_in_the_menu():
    menu = {
        "week": 43,
        "days": {
            "mandag": FIVE_DAY_MENU["days"]["mandag"],
            "fredag": FIVE_DAY_MENU["days"]["fredag"],
        },
    }

    view = week_view(menu, date(2026, 11, 18))

    assert [entry["is_today"] for entry in view] == [False, False]


def test_week_view_ignores_the_week_number():
    wednesday = date(2026, 11, 18)
    assert wednesday.isocalendar().week != FIVE_DAY_MENU["week"]

    view = by_day(week_view(FIVE_DAY_MENU, wednesday))

    assert view["onsdag"]["is_today"] is True


def test_week_view_marks_a_weekend_entry_on_its_day():
    menu = {
        "week": 43,
        "days": {
            "fredag": FIVE_DAY_MENU["days"]["fredag"],
            "lørdag": [{"name": "Brunsj", "price": 130, "allergens": ["egg"]}],
        },
    }

    view = by_day(week_view(menu, date(2026, 11, 21)))

    assert view["lørdag"]["is_today"] is True
    assert view["fredag"]["is_today"] is False
