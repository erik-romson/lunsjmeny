import json

import pytest

from menu import days_in_order, load_menu, week_view


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 1, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu)

    assert view == [{"day": "mandag", "dishes": [{"name": "Suppe", "price": 80, "allergens": []}]}]


WEEK = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag"]


def menu_with_days(days):
    return {"week": 1, "days": {day: [{"name": f"Rett {day}", "price": 90, "allergens": []}] for day in days}}


@pytest.mark.parametrize(
    "file_order",
    [
        ["fredag", "mandag", "onsdag", "tirsdag", "torsdag"],
        ["fredag", "torsdag", "onsdag", "tirsdag", "mandag"],
    ],
)
def test_days_come_in_week_order_whatever_the_order_in_the_file(tmp_path, file_order):
    menu_file = tmp_path / "menu.json"
    menu_file.write_text(json.dumps(menu_with_days(file_order), ensure_ascii=False), encoding="utf-8")

    view = week_view(load_menu(menu_file))

    assert [entry["day"] for entry in view] == WEEK
    for entry in view:
        assert entry["dishes"] == [{"name": f"Rett {entry['day']}", "price": 90, "allergens": []}]


def test_a_week_with_missing_days_keeps_week_order():
    menu = menu_with_days(["onsdag", "fredag", "mandag"])

    assert days_in_order(menu) == ["mandag", "onsdag", "fredag"]


def test_weekend_and_unknown_names_come_after_the_weekdays():
    menu = menu_with_days(["tirsdg", "søndag", "fredag", "lørdag", "Mandag", "mandag"])

    assert days_in_order(menu) == ["mandag", "fredag", "lørdag", "søndag", "Mandag", "tirsdg"]
