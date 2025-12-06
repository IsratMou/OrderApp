# orders/admin.py

from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem, ProductKeyword, ColorOption


class OrderItemInline(admin.TabularInline):
    """
    Order edit page er vitore direct product line gulo dekhano/edit korar jonno.
    """
    model = OrderItem
    extra = 0
    min_num = 0
    fields = ("product_keyword", "quantity", "color", "amount")
    show_change_link = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Main Order list & detail admin.
    Client jeno easily order khujte, filter korte pare.
    """

    # List page e kon kolam dekhabe
    list_display = (
        "id",
        "customer_name",
        "phone",
        "short_address",
        "items_count",
        "delivery_area",
        "items_subtotal",
        "delivery_charge",
        "total_amount",
        "created_at",
    )

    # Kon kolam clickable hobe
    list_display_links = ("id", "customer_name")

    # Right side e filter
    list_filter = ("delivery_area", "created_at")

    # Search box e kon field diye search hobe
    search_fields = ("customer_name", "phone", "address")

    # Date hierarchy (upore date navigation)
    date_hierarchy = "created_at"

    # Default order: newest first
    ordering = ("-created_at",)

    # Order detail page e inline items
    inlines = [OrderItemInline]

    # Detail page form order (section wise)
    fieldsets = (
        ("Customer", {
            "fields": ("customer_name", "phone", "address"),
        }),
        ("Delivery", {
            "fields": ("delivery_area", "delivery_charge"),
        }),
        ("Amounts", {
            "fields": ("items_subtotal", "total_amount"),
        }),
        ("Extra", {
            "fields": ("extra_info", "created_at"),
        }),
    )

    # created_at normally change kora lage na
    readonly_fields = ("created_at",)

    @admin.display(description="Items")
    def items_count(self, obj):
        """
        Order e mot koyta product line ache.
        """
        return obj.items.count()

    @admin.display(description="Address", ordering="address")
    def short_address(self, obj):
        """
        Address choto kore list view te show.
        """
        if not obj.address:
            return ""
        text = obj.address.strip()
        if len(text) > 40:
            return text[:37] + "..."
        return text


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Direct OrderItem list (rarely use, but thakle bhalo).
    """
    list_display = ("product_keyword", "quantity", "color", "amount", "order")
    search_fields = ("product_keyword", "color",
                     "order__customer_name", "order__phone")
    list_filter = ("color",)
    ordering = ("-id",)


@admin.register(ProductKeyword)
class ProductKeywordAdmin(admin.ModelAdmin):
    """
    Quick keyword button gulo manage korar jonno admin.
    """
    list_display = ("name", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("name",)
    ordering = ("sort_order", "name")


@admin.register(ColorOption)
class ColorOptionAdmin(admin.ModelAdmin):
    """
    Color preset gulo manage korar jonno admin.
    """
    list_display = ("name", "css_class", "is_active", "sort_order")
    list_editable = ("css_class", "is_active", "sort_order")
    search_fields = ("name",)
    ordering = ("sort_order", "name")
