from django.db import models
from django.contrib.auth.models import User
from django.db import models

class MenuItem(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=35)
    is_veg = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_images/')
    def __str__(self):
        return f"{self.name} ({'Veg' if self.is_veg else 'Non-veg'})"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'phone'], name='unique_customer')
        ]


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return sum(line.line_total for line in self.lines.all())

    def __str__(self):
        return f"Order #{self.pk}"

class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

    @property
    def line_total(self):
        return self.item.price * self.qty

    def __str__(self):
        return f"{self.qty} × {self.item.name}"
