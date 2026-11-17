"""The web page for the week's lunch menu."""

from flask import Flask, render_template, request

from menu import (
    allergen_choices,
    excluded_allergens,
    load_menu,
    unmatched_allergens,
    week_view,
)

app = Flask(__name__)


@app.get("/")
def index():
    menu = load_menu()
    excluded = excluded_allergens(request.args.getlist("uten"))
    return render_template(
        "index.html",
        week=menu["week"],
        days=week_view(menu, excluded),
        choices=allergen_choices(menu, excluded),
        excluded=excluded,
        unmatched=unmatched_allergens(menu, excluded),
    )
