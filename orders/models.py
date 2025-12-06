from decimal import Decimal
from django.db import models


class ProductKeyword(models.Model):
    """Quick product keyword buttons er jonno."""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class ColorOption(models.Model):
    """Quick color buttons er jonno."""
    name = models.CharField(max_length=50, unique=True)
    # Optional: tailwind class jate button er color change kora jay (e.g. 'bg-red-100 text-red-800')
    css_class = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Order(models.Model):
    DELIVERY_AREA_INSIDE = 'inside_dhaka'
    DELIVERY_AREA_SUB = 'dhaka_sub_area'
    DELIVERY_AREA_OUTSIDE = 'outside_dhaka'

    DELIVERY_AREA_CHOICES = [
        (DELIVERY_AREA_INSIDE, 'Inside Dhaka'),
        (DELIVERY_AREA_SUB, 'Dhaka sub-area'),
        (DELIVERY_AREA_OUTSIDE, 'Outside Dhaka'),
    ]

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    delivery_area = models.CharField(
        max_length=20,
        choices=DELIVERY_AREA_CHOICES,
        default=DELIVERY_AREA_INSIDE,
    )
    # Auto set hobe 60/100/120, but DB te store rakhlam
    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('60.00'),
    )
    # Sob product line er amount er sum (shipping chara)
    items_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    # Final total (items + delivery - discount) -> user editable
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Final total after delivery charge and any discount.",
    )

    extra_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.phone} ({self.created_at:%Y-%m-%d %H:%M})"

    @property
    def computed_auto_total(self):
        """Items subtotal + delivery charge (discount chara)."""
        return (self.items_subtotal or Decimal('0')) + (self.delivery_charge or Decimal('0'))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product_keyword = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True)
    # Ei amount holo oi line er total (qty * unit price jodi thake)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_keyword} x {self.quantity} ({self.order.customer_name})"
