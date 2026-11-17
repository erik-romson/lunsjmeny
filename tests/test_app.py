from app import app

TEST_MENU = {
    "week": 7,
    "days": {
        "mandag": [
            {"name": "Fiskesuppe", "price": 95, "allergens": ["fisk", "melk", "gluten"]},
            {"name": "Linsegryte", "price": 85, "allergens": ["selleri"]},
        ],
        "tirsdag": [
            {"name": "Kyllingtaco", "price": 99, "allergens": ["gluten", "melk"]},
            {"name": "Bønnetaco", "price": 89, "allergens": ["gluten"]},
        ],
        "onsdag": [
            {"name": "Pasta med pesto", "price": 92, "allergens": ["gluten", "nøtter", "melk"]},
            {"name": "Ris", "price": 50, "allergens": []},
            {"name": "Dagens gryte", "price": 90},
        ],
    },
}


ALL_DISHES = [
    "Fiskesuppe",
    "Linsegryte",
    "Kyllingtaco",
    "Bønnetaco",
    "Pasta med pesto",
    "Ris",
    "Dagens gryte",
]
ALL_HIDDEN = "Alle retter denne dagen inneholder allergener du har valgt bort."
UNMATCHED = "Ingen retter denne uken er merket med"


def get_page(monkeypatch, url, menu=TEST_MENU, **kwargs):
    monkeypatch.setattr("app.load_menu", lambda: menu)
    return app.test_client().get(url, **kwargs)


def day_section(page, heading):
    return page.split(f"<h2>{heading}</h2>")[1].split("</section>")[0]


def test_page_shows_the_week_and_a_dish():
    client = app.test_client()

    response = client.get("/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Lunsjmeny uke 43" in page
    assert "Fiskesuppe med brød" in page


def test_page_shows_the_allergens_of_each_dish(monkeypatch):
    response = get_page(monkeypatch, "/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Allergener: fisk, melk, gluten" in page
    assert "Allergener: selleri" in page


def test_page_says_when_a_dish_has_no_allergens(monkeypatch):
    response = get_page(monkeypatch, "/")

    page = response.get_data(as_text=True)
    assert "Ingen allergener registrert" in page


def test_page_says_when_allergens_are_not_stated(monkeypatch):
    response = get_page(monkeypatch, "/")

    page = response.get_data(as_text=True)
    assert "Dagens gryte" in page
    assert "Allergener ikke oppgitt" in page


def test_filter_hides_dishes_with_any_selected_allergen(monkeypatch):
    response = get_page(monkeypatch, "/?uten=gluten&uten=melk")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    for name in ["Fiskesuppe", "Kyllingtaco", "Bønnetaco", "Pasta med pesto", "Dagens gryte"]:
        assert name not in page
    assert "Linsegryte" in page
    assert "Ris" in page


def test_filter_shows_a_text_for_a_day_with_every_dish_hidden(monkeypatch):
    response = get_page(monkeypatch, "/?uten=gluten")

    page = response.get_data(as_text=True)
    assert ALL_HIDDEN in day_section(page, "Tirsdag")
    assert page.count(ALL_HIDDEN) == 1
    assert "Linsegryte" in page


def test_filter_can_empty_several_days(monkeypatch):
    response = get_page(
        monkeypatch,
        "/?uten=fisk&uten=melk&uten=gluten&uten=selleri&uten=nøtter",
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert page.count(ALL_HIDDEN) == 2
    assert "Ris" in page
    for name in ALL_DISHES:
        if name != "Ris":
            assert name not in page


def test_page_without_selection_shows_everything(monkeypatch):
    response = get_page(monkeypatch, "/")

    page = response.get_data(as_text=True)
    for name in ALL_DISHES:
        assert name in page
    assert ALL_HIDDEN not in page
    assert UNMATCHED not in page
    assert " checked>" not in page
    assert ">Vis alle retter</a>" not in page


def test_page_has_a_get_form_with_a_checkbox_per_allergen(monkeypatch):
    plain = get_page(monkeypatch, "/").get_data(as_text=True)
    selected = get_page(monkeypatch, "/?uten=gluten&uten=melk").get_data(as_text=True)

    assert 'method="get"' in plain
    assert 'action="/"' in plain
    assert 'name="uten" value="fisk">' in plain
    assert 'name="uten" value="nøtter">' in plain
    assert 'name="uten" value="gluten" checked>' in selected
    assert 'name="uten" value="melk" checked>' in selected
    assert 'name="uten" value="fisk">' in selected
    assert 'href="/">Vis alle retter</a>' in selected


def test_selection_ignores_case_and_surrounding_space(monkeypatch):
    for url in ["/?uten=GLUTEN", "/?uten=%20Gluten%20"]:
        response = get_page(monkeypatch, url)

        page = response.get_data(as_text=True)
        assert "Kyllingtaco" not in page
        assert 'name="uten" value="gluten" checked>' in page


def test_selection_matches_an_encoded_or_raw_non_ascii_label(monkeypatch):
    encoded = get_page(monkeypatch, "/?uten=n%C3%B8tter").get_data(as_text=True)
    raw = get_page(
        monkeypatch, "/", query_string={"uten": "nøtter"}
    ).get_data(as_text=True)

    for page in [encoded, raw]:
        assert "Pasta med pesto" not in page
        assert 'name="uten" value="nøtter" checked>' in page


def test_empty_selection_value_filters_nothing(monkeypatch):
    response = get_page(monkeypatch, "/?uten=")

    page = response.get_data(as_text=True)
    for name in ALL_DISHES:
        assert name in page
    assert UNMATCHED not in page
    assert " checked>" not in page
    assert "Vis alle retter" not in page


def test_unmatched_value_gets_a_notice_and_stays_ticked(monkeypatch):
    response = get_page(monkeypatch, "/?uten=hvete&uten=gluten")

    page = response.get_data(as_text=True)
    assert f"{UNMATCHED}: hvete." in page
    assert "Kyllingtaco" not in page
    assert 'name="uten" value="hvete" checked>' in page
    assert 'name="uten" value="gluten" checked>' in page


def test_undecodable_value_is_kept_literally_and_reported(monkeypatch):
    response = get_page(monkeypatch, "/?uten=n%F8tter")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Pasta med pesto" in page
    assert f"{UNMATCHED}: n%f8tter." in page


def test_a_day_without_dishes_in_the_data_gets_no_all_hidden_text(monkeypatch):
    menu = {
        "week": 7,
        "days": {
            "mandag": [{"name": "Taco", "price": 90, "allergens": ["gluten"]}],
            "tirsdag": [],
        },
    }

    response = get_page(monkeypatch, "/?uten=gluten", menu=menu)

    page = response.get_data(as_text=True)
    assert page.count(ALL_HIDDEN) == 1
    assert ALL_HIDDEN not in day_section(page, "Tirsdag")


def test_html_in_the_selection_is_escaped(monkeypatch):
    response = get_page(monkeypatch, "/?uten=%22%3E%3Cscript%3Ealert(1)%3C%2Fscript%3E")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
