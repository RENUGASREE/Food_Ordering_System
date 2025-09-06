from django.contrib import admin
from .models import MenuItem, Customer, Order, OrderLine
class OrderLineInline(admin.TabularInline):
    model = OrderLine; extra = 1; autocomplete_fields = ('item',)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderLineInline]; list_display = ('id','customer','created_at','subtotal'); search_fields = ('customer__name','customer__phone'); list_filter = ('created_at',)
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id','name','price','category','is_veg'); list_filter = ('category','is_veg'); search_fields = ('name','category')
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name','phone'); search_fields = ('name','phone')
@admin.register(OrderLine)
class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('order','item','qty','line_total'); list_filter = ('item',)
