# Foodies (Updated)

What I changed:
- Veg/non-veg toggles on Menu
- Flash messages for signup/login/checkout/cart
- Clean login/signup templates
- Checkout asks for Name + **Phone (required)**; logged-in users are prefilled from their Customer profile or last order.
- Receipt page with **Download PDF** (ReportLab)
- `Customer` now links to `User` (optional) and has unique constraint on (name, phone)

## How to run
```bash
pip install -r requirements.txt  # if you have one
pip install reportlab            # needed for PDF receipts
python manage.py makemigrations orders
python manage.py migrate
python manage.py runserver
```

## Notes
- If you already created duplicate `Guest / N/A` customers, clean them in the Django shell:
```py
from orders.models import Customer
Customer.objects.filter(name="Guest", phone="N/A").delete()
Customer.objects.get_or_create(name="Guest", phone="N/A")
```
- If you changed the `Customer` model from before, you must run migrations.
- URLs:
  - `/` or `/menu/` – browse
  - `/cart/` – cart
  - `/checkout/` – checkout
  - `/login/`, `/signup/`, `/logout/`
  - `/receipt/<order_id>/` + `/receipt/<order_id>/pdf/`
