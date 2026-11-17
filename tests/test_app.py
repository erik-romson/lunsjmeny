import re

from app import app


def test_page_shows_the_week_and_a_dish():
    client = app.test_client()

    response = client.get("/")

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Lunsjmeny uke 43" in page
    assert "Fiskesuppe med brød" in page


def test_page_lists_the_days_from_mandag_to_fredag(monkeypatch):
    days = ["fredag", "mandag", "onsdag", "tirsdag", "torsdag"]
    shuffled = {"week": 43, "days": {day: [{"name": f"Rett {day}", "price": 90, "allergens": []}] for day in days}}
    monkeypatch.setattr("app.load_menu", lambda: shuffled)

    page = app.test_client().get("/").get_data(as_text=True)

    assert re.findall(r"<h2>(.*?)</h2>", page) == ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"]
