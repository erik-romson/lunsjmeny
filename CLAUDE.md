# Lunsjmeny

A Flask page that shows the week's lunch menu from `menu.json`.

- `menu.py` holds the logic and does not import Flask. Test it with plain functions.
- `app.py` and `templates/index.html` make the page.
- Run the tests: `uv run pytest -q`.
- Run the page: `uv run flask --app app run --port 8000`. Use another port in each clone.
- Page text is Norwegian bokmål. Code, names and comments are English.
