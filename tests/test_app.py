from flask import render_template

from app import app


def test_page_shows_the_week_and_a_dish():
    client = app.test_client()

    response = client.get("/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Lunsjmeny uke 43" in page
    assert "Fiskesuppe med brød" in page


def test_each_dish_shows_its_allergens():
    client = app.test_client()

    response = client.get("/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Allergener: fisk, melk, gluten" in page
    assert "Allergener: soya, sesam" in page


def test_a_dish_without_allergens_shows_ingen():
    days = [{"day": "mandag", "dishes": [{"name": "Salat", "price": 70, "allergens": []}]}]

    with app.test_request_context("/"):
        page = render_template("index.html", week=1, days=days, allergens=[], selected=[])

    assert "Allergener: ingen" in page


EMPTY_DAY_TEXT = "Alle rettene denne dagen inneholder valgte allergener."


def test_chosen_allergens_in_the_address_hide_dishes():
    client = app.test_client()

    response = client.get("/?uten=gluten&uten=melk")

    page = response.get_data(as_text=True)
    for hidden in [
        "Fiskesuppe med brød",
        "Kyllingtaco",
        "Bønnetaco",
        "Kjøttkaker med brun saus",
        "Pasta med pesto",
        "Pizza margherita",
    ]:
        assert hidden not in page
    for kept in [
        "Linsegryte med ris",
        "Ovnsbakt laks med poteter",
        "Ertesuppe med flesk",
        "Pokebowl med tofu",
    ]:
        assert kept in page


def test_a_day_where_every_dish_is_hidden_shows_a_short_text():
    client = app.test_client()

    response = client.get("/?uten=gluten")

    page = response.get_data(as_text=True)
    assert page.count(EMPTY_DAY_TEXT) == 1
    assert page.count("<ul>") == 4
    assert "Kyllingtaco" not in page
    assert "Bønnetaco" not in page


def test_every_day_shows_the_text_when_every_dish_is_hidden():
    client = app.test_client()
    everything = ["egg", "fisk", "gluten", "melk", "nøtter", "selleri", "sesam", "soya"]

    response = client.get("/", query_string={"uten": everything})

    page = response.get_data(as_text=True)
    assert page.count(EMPTY_DAY_TEXT) == 5
    assert "<ul>" not in page


def test_the_chosen_allergens_are_ticked_in_the_form():
    client = app.test_client()

    response = client.get("/?uten=gluten&uten=melk")

    page = response.get_data(as_text=True)
    assert 'name="uten" value="gluten" checked>' in page
    assert 'name="uten" value="melk" checked>' in page
    assert 'name="uten" value="fisk">' in page
    assert page.count("checked") == 2


def test_the_form_offers_this_weeks_allergens_and_sends_them_as_uten():
    client = app.test_client()
    names = ["egg", "fisk", "gluten", "melk", "nøtter", "selleri", "sesam", "soya"]

    response = client.get("/")

    page = response.get_data(as_text=True)
    positions = [page.index(f'name="uten" value="{name}">') for name in names]
    assert 'method="get"' in page
    assert positions == sorted(set(positions))
    assert "checked" not in page


def test_allergen_names_in_the_address_ignore_case_and_spaces():
    client = app.test_client()

    response = client.get("/?uten=%20Gluten%20")

    page = response.get_data(as_text=True)
    assert "Bønnetaco" not in page
    assert "Linsegryte med ris" in page
    assert 'name="uten" value="gluten" checked>' in page


def test_an_allergen_with_a_non_ascii_name_works_in_the_address():
    client = app.test_client()

    response = client.get("/?uten=n%C3%B8tter")

    page = response.get_data(as_text=True)
    assert "Pasta med pesto" not in page
    assert "Ertesuppe med flesk" in page
    assert 'name="uten" value="nøtter" checked>' in page


def test_empty_or_unknown_allergens_in_the_address_hide_nothing():
    client = app.test_client()

    response = client.get("/?uten=&uten=pean%C3%B8tter&uten=%3Cscript%3E")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Fiskesuppe med brød" in page
    assert "Pasta med pesto" in page
    assert "Pokebowl med tofu" in page
    assert "checked" not in page
    assert "peanøtter" not in page
    assert "<script>" not in page
