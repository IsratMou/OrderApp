from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'phone', 'created_at')
    search_fields = ('customer_name', 'phone')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product_keyword', 'quantity', 'color', 'amount', 'order')
    search_fields = ('product_keyword', 'color')
