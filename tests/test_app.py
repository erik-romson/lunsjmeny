from datetime import date

import app as app_module
from app import app

PAGE_MENU = {
    "week": 43,
    "days": {
        "mandag": [{"name": "Kjøttkaker i brun saus", "price": 125, "allergens": ["gluten"]}],
        "onsdag": [{"name": "Laksefilet med poteter", "price": 135, "allergens": ["fisk"]}],
        "fredag": [{"name": "Vegetarlasagne", "price": 120, "allergens": ["gluten", "melk"]}],
    },
}


def page_on(monkeypatch, day):
    monkeypatch.setattr(app_module, "load_menu", lambda: PAGE_MENU)
    monkeypatch.setattr(app_module, "today", lambda: day)

    response = app_module.app.test_client().get("/")

    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_page_shows_the_week_and_a_dish():
    client = app.test_client()

    response = client.get("/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Lunsjmeny uke 43" in page
    assert "Fiskesuppe med brød" in page


def test_page_highlights_wednesday_on_a_wednesday(monkeypatch):
    page = page_on(monkeypatch, date(2026, 11, 18))

    assert page.count('class="day today"') == 1
    assert page.count('aria-current="date"') == 1
    assert page.count("I dag") == 1
    start = page.index('class="day today"')
    highlighted = page[start : page.index("</section>", start)]
    assert "Onsdag" in highlighted
    assert 'class="today-label">I dag<' in highlighted
    assert "Laksefilet med poteter" in highlighted
    assert "Kjøttkaker i brun saus" not in highlighted
    assert "Vegetarlasagne" not in highlighted


def test_page_highlights_nothing_on_a_saturday(monkeypatch):
    page = page_on(monkeypatch, date(2026, 11, 21))

    assert 'class="day today"' not in page
    assert 'aria-current="date"' not in page
    assert "I dag" not in page
    assert "Kjøttkaker i brun saus" in page
    assert "Laksefilet med poteter" in page
    assert "Vegetarlasagne" in page


def test_stylesheet_styles_the_highlighted_day():
    response = app_module.app.test_client().get("/static/style.css")

    try:
        assert response.status_code == 200
        css = response.get_data(as_text=True)
        assert ".day.today" in css
        assert ".today-label" in css
    finally:
        response.close()
