from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Prefetch
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.html import format_html
from django.http import HttpResponse

from .models import MenuItem, Order, OrderLine, Customer
from .forms import AddToCartForm, CustomerForm, SignUpForm
from .pricing import compute_adjustments, compute_total

# PDF
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _get_or_create_order(request):
    order_id = request.session.get("order_id")
    order = None
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            order = None
    if not order:
        # Create a placeholder customer until checkout
        customer, _ = Customer.objects.get_or_create(name="Guest", phone="N/A")
        order = Order.objects.create(customer=customer)
        request.session["order_id"] = order.id
    return order


def menu(request):
    # Optional filters
    category = request.GET.get("category")
    only_veg = request.GET.get("veg") == "1"
    only_nonveg = request.GET.get("nonveg") == "1"

    qs = MenuItem.objects.all()

    if category:
        qs = qs.filter(category=category)
    if only_veg:
        qs = qs.filter(is_veg=True)
    if only_nonveg:
        qs = qs.filter(is_veg=False)

    # Group by category
    grouped = {}
    for item in qs.order_by("category", "name"):
        grouped.setdefault(item.category, []).append(item)

    form = AddToCartForm()
    categories = list(MenuItem.objects.values_list("category", flat=True).distinct())

    context = {
        "grouped": grouped,
        "form": form,
        "categories": categories,
        "active_category": category,
        "only_veg": only_veg,
        "only_nonveg": only_nonveg,
    }
    return render(request, "orders/menu.html", context)


def add_to_cart(request):
    if request.method != "POST":
        return redirect("menu")
    form = AddToCartForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid input.")
        return redirect("menu")
    item = get_object_or_404(MenuItem, id=form.cleaned_data["item_id"])
    qty = form.cleaned_data["qty"]
    order = _get_or_create_order(request)
    line, created = OrderLine.objects.get_or_create(
        order=order, item=item, defaults={"qty": qty}
    )
    if not created:
        line.qty += qty
        line.save()
    messages.success(request, f"Added {qty} × {item.name} to cart.")
    return redirect("cart")


def cart(request):
    order = _get_or_create_order(request)
    order = Order.objects.prefetch_related(
        Prefetch("lines", queryset=OrderLine.objects.select_related("item"))
    ).get(id=order.id)
    adjustments = compute_adjustments(order)
    total = compute_total(order)
    return render(
        request,
        "orders/cart.html",
        {"order": order, "adjustments": adjustments, "total": total},
    )


def update_qty(request):
    if request.method != "POST":
        return redirect("cart")
    order = _get_or_create_order(request)
    line_id = request.POST.get("line_id")
    qty = int(request.POST.get("qty", "1"))
    line = get_object_or_404(OrderLine, id=line_id, order=order)
    if qty <= 0:
        line.delete()
        messages.info(request, "Item removed from cart.")
    else:
        line.qty = qty
        line.save()
        messages.success(request, "Quantity updated.")
    return redirect("cart")


def _prefill_customer_initial(request, order):
    # If logged-in, try existing customer by user, else last order
    if request.user.is_authenticated:
        try:
            c = Customer.objects.get(user=request.user)
            return {"name": c.name, "phone": c.phone}
        except Customer.DoesNotExist:
            # fallback from last order linked to any customer of the user (if such exist)
            last = Order.objects.filter(customer__user=request.user).order_by("-id").first()
            if last and last.customer:
                return {"name": last.customer.name, "phone": last.customer.phone}
            # fallback to username
            return {"name": request.user.get_full_name() or request.user.username, "phone": ""}
    else:
        # prefill from the order's current customer if it's not the default Guest
        if order.customer and (order.customer.name != "Guest" or order.customer.phone != "N/A"):
            return {"name": order.customer.name, "phone": order.customer.phone}
        return {"name": "", "phone": ""}


def checkout(request):
    order = _get_or_create_order(request)
    order = Order.objects.prefetch_related(
        Prefetch("lines", queryset=OrderLine.objects.select_related("item"))
    ).get(id=order.id)
    if not order.lines.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("menu")

    adjustments = compute_adjustments(order)
    total = compute_total(order)

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"].strip() or "Guest"
            phone = form.cleaned_data["phone"].strip()

            if request.user.is_authenticated:
                customer, created = Customer.objects.get_or_create(user=request.user, defaults={"name": name, "phone": phone})
                # Keep profile fresh
                customer.name = name
                customer.phone = phone
                customer.save()
            else:
                customer, _ = Customer.objects.get_or_create(name=name, phone=phone)

            order.customer = customer
            order.save()

            # Clear the cart session but keep id for redirect via url
            request.session["order_id"] = None

            # Success message with PDF link
            pdf_url = f"/receipt/{order.id}/pdf/"
            msg = format_html(
                'Checkout successful! 🎉 <a href="{}" class="btn btn-sm btn-success ms-2">Download Receipt (PDF)</a>',
                pdf_url,
            )
            messages.success(request, msg)

            return redirect("receipt", order_id=order.id)
        else:
            # invalid form
            return render(request, "orders/checkout.html", {"order": order, "form": form, "adjustments": adjustments, "total": total})
    else:
        initial = _prefill_customer_initial(request, order)
        form = CustomerForm(initial=initial)

    return render(
        request,
        "orders/checkout.html",
        {"order": order, "form": form, "adjustments": adjustments, "total": total},
    )


# ---------------- AUTH ---------------- #

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful! Welcome 🎉")
            return redirect("menu")
        else:
            messages.error(request, "Signup failed. Please check the form.")
    else:
        form = SignUpForm()
    return render(request, "orders/registration/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username} 👋")
            return redirect("menu")

    else:
        form = AuthenticationForm()
    return render(request, "orders/registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("menu")


# ---------------- RECEIPT ---------------- #

def receipt(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            Prefetch("lines", queryset=OrderLine.objects.select_related("item"))
        ),
        id=order_id,
    )
    adjustments = compute_adjustments(order)
    total = compute_total(order)
    return render(
        request,
        "orders/receipt.html",
        {"order": order, "adjustments": adjustments, "total": total},
    )


def receipt_pdf(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            Prefetch("lines", queryset=OrderLine.objects.select_related("item"))
        ),
        id=order_id,
    )
    adjustments = compute_adjustments(order)
    total = compute_total(order)

    # PDF setup
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Foodies Receipt")
    y -= 40

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Order ID: {order.id}")
    y -= 20
    p.drawString(50, y, f"Customer: {order.customer.name}")
    y -= 20
    p.drawString(50, y, f"Phone: {order.customer.phone}")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Items")
    y -= 20

    p.setFont("Helvetica", 11)
    for line in order.lines.all():
        p.drawString(60, y, f"{line.qty} × {line.item.name}")
        p.drawRightString(width - 60, y, f"₹{line.line_total}")
        y -= 20
        if y < 80:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Items (cont.)")
            y -= 20
            p.setFont("Helvetica", 11)

    y -= 10
    p.drawString(50, y, f"Subtotal: ₹{order.subtotal}")
    y -= 20
    for label, delta in adjustments:
        if delta:
            p.drawString(50, y, f"{label}:")
            p.drawRightString(width - 60, y, f"₹{delta}")
            y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Grand Total: ₹{total}")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="receipt_{order.id}.pdf"'
    return response
