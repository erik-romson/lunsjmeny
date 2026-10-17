from datetime import date

import app as app_module
from app import app

MENU = {"week": 43, "days": {
    "mandag": [{"name": "Fiskesuppe", "price": 95, "allergens": []}],
    "tirsdag": [{"name": "Kyllingtaco", "price": 99, "allergens": []}],
}}


def page_on(monkeypatch, day):
    monkeypatch.setattr(app_module, "load_menu", lambda: MENU)
    monkeypatch.setattr(app_module, "today", lambda: day)
    response = app.test_client().get("/")
    assert response.status_code == 200
    return response.get_data(as_text=True)


def test_page_shows_the_week_and_a_dish():
    client = app.test_client()

    response = client.get("/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Lunsjmeny uke 43" in page
    assert "Fiskesuppe med brød" in page


def test_page_highlights_today_on_a_weekday(monkeypatch):
    page = page_on(monkeypatch, date(2026, 10, 20))

    assert page.count('class="day today"') == 1
    assert page.count('aria-current="date"') == 1
    highlighted = page.split('class="day today"', 1)[1].split("</section>", 1)[0]
    assert 'aria-current="date"' in highlighted
    assert "Tirsdag" in highlighted
    assert 'class="today-label">I dag<' in highlighted
    assert "Kyllingtaco" in highlighted
    assert "Fiskesuppe" not in highlighted
    assert page.count("I dag") == 1


def test_page_highlights_no_day_on_a_weekend(monkeypatch):
    page = page_on(monkeypatch, date(2026, 10, 24))

    assert 'aria-current="date"' not in page
    assert "I dag" not in page
    assert 'class="day today"' not in page
    assert "Fiskesuppe" in page
    assert "Kyllingtaco" in page


def test_stylesheet_styles_the_highlight():
    response = app.test_client().get("/static/style.css")

    assert response.status_code == 200
    css = response.get_data(as_text=True)
    assert ".day.today" in css
    assert ".today-label" in css
