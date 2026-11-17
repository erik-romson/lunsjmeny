import copy

from menu import (
    allergen_choices,
    dish_allergens,
    excluded_allergens,
    is_hidden,
    load_menu,
    normalize_allergen,
    unmatched_allergens,
    week_allergens,
    week_view,
)


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 1, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu)

    assert view == [
        {
            "day": "mandag",
            "dishes": [{"name": "Suppe", "price": 80, "allergens": []}],
            "all_hidden": False,
        }
    ]


def test_normalize_allergen_strips_casefolds_and_composes():
    decomposed = "å"

    assert normalize_allergen("  Gluten ") == "gluten"
    assert normalize_allergen("NØTTER") == "nøtter"
    assert normalize_allergen(decomposed) == "å"
    assert normalize_allergen(decomposed) != decomposed


def test_excluded_allergens_normalises_and_drops_empty_values():
    assert excluded_allergens(["gluten", "melk"]) == frozenset({"gluten", "melk"})
    assert excluded_allergens([]) == frozenset()
    assert excluded_allergens(["", "  ", "gluten"]) == frozenset({"gluten"})
    assert excluded_allergens(["Gluten", "gluten"]) == frozenset({"gluten"})
    assert excluded_allergens(["gluten,melk"]) == frozenset({"gluten,melk"})


def test_dish_allergens_distinguishes_declared_none_from_not_stated():
    assert dish_allergens({"allergens": ["Fisk", " melk", "fisk", ""]}) == ["fisk", "melk"]
    assert dish_allergens({"allergens": []}) == []
    assert dish_allergens({}) is None
    assert dish_allergens({"allergens": None}) is None
    assert dish_allergens({"allergens": "gluten"}) is None
    assert dish_allergens({"allergens": ["gluten", 3]}) is None


def test_is_hidden_matches_exact_labels_and_hides_unstated_dishes():
    assert is_hidden({"allergens": ["fisk", "melk", "gluten"]}, frozenset({"melk"})) is True
    assert is_hidden({"allergens": ["selleri"]}, frozenset({"gluten", "melk"})) is False
    assert is_hidden({"allergens": ["gluten"]}, frozenset()) is False
    assert is_hidden({}, frozenset({"gluten"})) is True
    assert is_hidden({}, frozenset()) is False
    assert is_hidden({"allergens": []}, frozenset({"gluten"})) is False
    assert is_hidden({"allergens": ["eggehvite"]}, frozenset({"egg"})) is False
    assert is_hidden({"allergens": ["Gluten"]}, frozenset({"gluten"})) is True


def _filter_menu() -> dict:
    return {
        "week": 1,
        "days": {
            "mandag": [
                {"name": "A", "price": 1, "allergens": ["gluten"]},
                {"name": "B", "price": 2, "allergens": ["selleri"]},
            ],
            "tirsdag": [{"name": "C", "price": 3, "allergens": ["gluten"]}],
            "onsdag": [],
            "torsdag": [{"name": "D", "price": 4}],
        },
    }


def test_week_view_drops_hidden_dishes_and_flags_emptied_days():
    menu = _filter_menu()

    view = {entry["day"]: entry for entry in week_view(menu, frozenset({"gluten"}))}

    assert view["mandag"]["dishes"] == [{"name": "B", "price": 2, "allergens": ["selleri"]}]
    assert view["mandag"]["all_hidden"] is False
    assert view["tirsdag"]["dishes"] == []
    assert view["tirsdag"]["all_hidden"] is True
    assert view["onsdag"]["dishes"] == []
    assert view["onsdag"]["all_hidden"] is False
    assert view["torsdag"]["dishes"] == []
    assert view["torsdag"]["all_hidden"] is True


def test_week_view_without_selection_keeps_dishes_with_unstated_allergens():
    menu = _filter_menu()

    view = {entry["day"]: entry for entry in week_view(menu)}

    assert view["torsdag"]["dishes"] == [{"name": "D", "price": 4, "allergens": None}]
    assert view["torsdag"]["all_hidden"] is False


def test_week_view_does_not_mutate_the_menu():
    menu = _filter_menu()
    before = copy.deepcopy(menu)

    week_view(menu, frozenset({"gluten"}))

    assert menu == before


def test_week_allergens_is_the_sorted_union_of_stated_labels():
    menu = {
        "week": 1,
        "days": {
            "mandag": [
                {"name": "A", "price": 1, "allergens": ["Gluten", "melk"]},
                {"name": "B", "price": 2, "allergens": ["gluten", "nøtter"]},
                {"name": "C", "price": 3},
            ]
        },
    }

    assert week_allergens(menu) == ["gluten", "melk", "nøtter"]


def test_allergen_choices_keep_selected_values_missing_from_the_week():
    menu = {
        "week": 1,
        "days": {"mandag": [{"name": "A", "price": 1, "allergens": ["gluten", "melk"]}]},
    }

    choices = allergen_choices(menu, frozenset({"skalldyr", "melk"}))

    assert choices == ["gluten", "melk", "skalldyr"]


def test_unmatched_allergens_lists_selected_values_not_on_the_menu():
    menu = {
        "week": 1,
        "days": {"mandag": [{"name": "A", "price": 1, "allergens": ["gluten", "melk"]}]},
    }

    unmatched = unmatched_allergens(menu, frozenset({"gluten", "hvete", "laktose"}))

    assert unmatched == ["hvete", "laktose"]
    assert unmatched_allergens(menu, frozenset()) == []


def test_every_dish_in_the_real_menu_has_a_list_of_allergen_labels():
    menu = load_menu()

    for day, dishes in menu["days"].items():
        for dish in dishes:
            where = f"{day}: {dish.get('name')}"
            assert isinstance(dish.get("allergens"), list), where
            assert all(isinstance(a, str) and a.strip() for a in dish["allergens"]), where
