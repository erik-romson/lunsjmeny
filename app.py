"""The web page for the week's lunch menu."""

from datetime import date

from flask import Flask, render_template

from menu import load_menu, week_view

app = Flask(__name__)


def today() -> date:
    """Return the server's local date. Tests replace this function."""
    return date.today()


@app.get("/")
def index():
    menu = load_menu()
    days = week_view(menu, today())
    return render_template("index.html", week=menu["week"], days=days)
