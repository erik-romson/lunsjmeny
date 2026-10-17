from menu import load_menu, week_view


def test_menu_has_a_week_number_and_five_days():
    menu = load_menu()

    assert menu["week"] == 43
    assert len(menu["days"]) == 5


def test_week_view_keeps_the_dishes_of_each_day():
    menu = {"week": 1, "days": {"mandag": [{"name": "Suppe", "price": 80, "allergens": []}]}}

    view = week_view(menu)

    assert view == [{"day": "mandag", "dishes": [{"name": "Suppe", "price": 80, "allergens": []}]}]
