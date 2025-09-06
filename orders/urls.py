from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.menu, name="menu"),
    path("menu/", views.menu, name="menu"),
    path("cart/", views.cart, name="cart"),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path("update-qty/", views.update_qty, name="update_qty"),
    path("checkout/", views.checkout, name="checkout"),

    path("receipt/<int:order_id>/", views.receipt, name="receipt"),
    path("receipt/<int:order_id>/pdf/", views.receipt_pdf, name="receipt_pdf"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),

] 
