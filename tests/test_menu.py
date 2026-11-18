import copy

import pytest

from menu import allergens_in_week, chosen_allergens, hide_dishes, load_menu, week_view


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 1, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu)

    assert view == [{"day": "mandag", "dishes": [{"name": "Suppe", "price": 80, "allergens": []}]}]


def test_chosen_allergens_trims_lowercases_and_drops_blanks_and_repeats():
    values = [" Gluten", "melk", "", "gluten", "MELK ", "  "]

    chosen = chosen_allergens(values)

    assert chosen == ["gluten", "melk"]


def test_allergens_in_week_lists_each_allergen_once_in_alphabetical_order():
    menu = {
        "week": 1,
        "days": {
            "mandag": [
                {"name": "Suppe", "price": 80, "allergens": ["melk", "Gluten"]},
                {"name": "Salat", "price": 70, "allergens": []},
            ],
            "tirsdag": [{"name": "Pesto", "price": 90, "allergens": ["soya", "nøtter", "melk"]}],
        },
    }

    allergens = allergens_in_week(menu)

    assert allergens == ["gluten", "melk", "nøtter", "soya"]


def test_hide_dishes_removes_every_dish_with_a_chosen_allergen():
    suppe = {"name": "Suppe", "price": 80, "allergens": ["melk"]}
    salat = {"name": "Salat", "price": 70, "allergens": []}
    brod = {"name": "Brød", "price": 40, "allergens": ["gluten"]}
    laks = {"name": "Laks", "price": 120, "allergens": ["fisk"]}
    menu = {"week": 1, "days": {"mandag": [suppe, salat, brod, laks]}}

    shown = hide_dishes(week_view(menu), ["gluten", "melk"])

    assert shown == [{"day": "mandag", "dishes": [salat, laks]}]


def test_hide_dishes_keeps_a_day_whose_dishes_are_all_hidden():
    suppe = {"name": "Suppe", "price": 80, "allergens": ["melk"]}
    taco = {"name": "Taco", "price": 90, "allergens": ["gluten"]}
    menu = {"week": 1, "days": {"mandag": [suppe], "tirsdag": [taco]}}

    shown = hide_dishes(week_view(menu), ["gluten"])

    assert shown == [{"day": "mandag", "dishes": [suppe]}, {"day": "tirsdag", "dishes": []}]


def test_hide_dishes_hides_nothing_when_nothing_or_only_unknown_allergens_are_chosen():
    menu = {
        "week": 1,
        "days": {
            "mandag": [
                {"name": "Suppe", "price": 80, "allergens": ["melk"]},
                {"name": "Salat", "price": 70, "allergens": []},
                {"name": "Brød", "price": 40, "allergens": ["gluten"]},
                {"name": "Laks", "price": 120, "allergens": ["fisk"]},
            ]
        },
    }
    days = week_view(menu)

    assert hide_dishes(days, []) == days
    assert hide_dishes(days, ["xyz"]) == days


def test_hide_dishes_ignores_case_and_spaces():
    menu = {"week": 1, "days": {"mandag": [{"name": "Brød", "price": 40, "allergens": ["Gluten"]}]}}

    shown = hide_dishes(week_view(menu), [" gluten "])

    assert shown == [{"day": "mandag", "dishes": []}]


def test_hide_dishes_leaves_its_input_unchanged():
    menu = {
        "week": 1,
        "days": {
            "mandag": [
                {"name": "Suppe", "price": 80, "allergens": ["melk"]},
                {"name": "Salat", "price": 70, "allergens": []},
                {"name": "Brød", "price": 40, "allergens": ["gluten"]},
                {"name": "Laks", "price": 120, "allergens": ["fisk"]},
            ]
        },
    }
    days = week_view(menu)
    before = copy.deepcopy(days)

    hide_dishes(days, ["melk"])

    assert days == before


def test_hide_dishes_fails_on_a_dish_without_allergens():
    days = [{"day": "mandag", "dishes": [{"name": "Suppe", "price": 80}]}]

    with pytest.raises(KeyError):
        hide_dishes(days, [])
