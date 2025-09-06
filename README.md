# Foodies — Django Food Ordering Website (Cleaned & Pro)

This is an improved, production‑ready version of your project with a neat structure, professional UI, and fixes for issues that caused runtime errors.

## What’s improved
- Removed broken placeholders and rebuilt `orders/forms.py`, `orders/views.py`, and `orders/pricing.py` (no more ellipses/parse errors).
- Fixed URL routing and auth template paths.
- Simplified requirements to only `Django>=4.2,<5`.
- Clean Bootstrap‑based UI with better layout and responsiveness.
- Added a small stylesheet in `static/app.css`.
- Safer defaults in `settings.py` including login redirects and a `STATIC_ROOT`.
- Kept your features (menu, cart, checkout, receipt). Added filters (Veg‑only, category) and inline quantity updates.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Initialize DB (uses SQLite)
python manage.py migrate

# (Optional) Create a superuser for /admin
python manage.py createsuperuser

# Run
python manage.py runserver
```

Open http://127.0.0.1:8000/ — you should see the menu. Use **Cart** and **Checkout** to place a test order.

> Tip: If your original `db.sqlite3` has data, it will be used. If you prefer a clean slate, delete `db.sqlite3` and run `migrate` again.

## Notes
- Bootstrap is loaded via CDN for convenience. You can replace it with a local copy if you must be completely offline.
- Static files for production can be collected with `python manage.py collectstatic` (they’ll go to `staticfiles/`).

Enjoy! 🎉
