from datetime import date

import pytest

import app as app_module
from app import app


def page_on(monkeypatch, day):
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


def test_page_highlights_only_todays_day(monkeypatch):
    page = page_on(monkeypatch, date(2026, 10, 21))

    assert page.count('class="day today"') == 1
    assert page.count('aria-current="date"') == 1
    assert page.count("I dag") == 1
    start = page.index('class="day today"')
    end = page.index("</section>", start)
    today_section = page[start:end]
    assert "Onsdag" in today_section
    assert "Kjøttkaker med brun saus" in today_section
    assert "Ovnsbakt laks med poteter" in today_section
    assert "Fiskesuppe med brød" not in today_section
    assert "Pizza margherita" not in today_section


@pytest.mark.parametrize("weekend_day", [date(2026, 10, 24), date(2026, 10, 25)])
def test_page_highlights_nothing_on_a_weekend(monkeypatch, weekend_day):
    page = page_on(monkeypatch, weekend_day)

    assert 'class="day today"' not in page
    assert "aria-current" not in page
    assert "I dag" not in page
    for day in ("Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"):
        assert day in page


def test_stylesheet_styles_the_highlight():
    response = app.test_client().get("/static/style.css")

    try:
        assert response.status_code == 200
        css = response.get_data(as_text=True)
        assert ".day.today" in css
        assert ".today-label" in css
    finally:
        response.close()
