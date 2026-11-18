"""The web page for the week's lunch menu."""

from flask import Flask, render_template, request

from menu import allergens_in_week, chosen_allergens, hide_dishes, load_menu, week_view

app = Flask(__name__)


@app.get("/")
def index():
    menu = load_menu()
    selected = chosen_allergens(request.args.getlist("uten"))
    return render_template(
        "index.html",
        week=menu["week"],
        days=hide_dishes(week_view(menu), selected),
        allergens=allergens_in_week(menu),
        selected=selected,
    )
