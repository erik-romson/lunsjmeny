"""The web page for the week's lunch menu."""

from flask import Flask, render_template

from menu import load_menu, week_view

app = Flask(__name__)


@app.get("/")
def index():
    menu = load_menu()
    return render_template("index.html", week=menu["week"], days=week_view(menu))
