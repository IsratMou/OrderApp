# orders/views.py

import json
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import OrderForm
from .models import (
    Order,
    OrderItem,
    ProductKeyword,
    ColorOption,
)

# Delivery charge map (same logic as template)
DELIVERY_CHARGES = {
    Order.DELIVERY_AREA_INSIDE: Decimal('60'),
    Order.DELIVERY_AREA_SUB: Decimal('100'),
    Order.DELIVERY_AREA_OUTSIDE: Decimal('120'),
}


def detect_delivery_area_from_address(address: str) -> str:
    """
    Address text diye roughly guess kore:
    - Inside Dhaka
    - Dhaka sub-area
    - Outside Dhaka
    Keyword list tumi nijer moto modify korte parba.
    """
    text = (address or '').lower()

    # Very rough list – ichchhe moto barate/modify korte paro
    inside_keywords = [
        'uttara', 'banani', 'dhanmondi', 'mirpur', 'badda',
        'motijheel', 'gulshan', 'mohakhali', 'shyamoli',
        'mohammadpur', 'tejgaon', 'farmgate', 'ramna',
        'kakrail', 'khilkhet', 'khilgaon', 'jatrabari',
        'rampura', 'malibagh', 'shantinagar', 'paltan',
        'bansree', 'uttarkhan', 'dakshinkhan', 'demra',
    ]
    sub_area_keywords = [
        'savar', 'ashulia', 'gazipur', 'tonggi', 'tonggi',
        'narayanganj', 'keraniganj', 'nobinagar', 'nabinagar',
        'joydebpur', 'joydevpur',
    ]

    if any(k in text for k in inside_keywords):
        return Order.DELIVERY_AREA_INSIDE
    if any(k in text for k in sub_area_keywords):
        return Order.DELIVERY_AREA_SUB
    return Order.DELIVERY_AREA_OUTSIDE


@require_http_methods(["GET", "POST"])
def new_order(request):
    items_error = None

    # items_json always define kortechi jate porer dike error na hoy
    if request.method == 'POST':
        items_json = request.POST.get('items_json', '[]').strip() or '[]'
    else:
        items_json = "[]"

    # Try to parse products JSON
    try:
        items_data = json.loads(items_json)
    except json.JSONDecodeError:
        items_data = []
        items_error = "Product list invalid. Please try again."

    if request.method == 'POST':
        if not items_data:
            items_error = "At least one product is required."

        form = OrderForm(request.POST)

        if form.is_valid() and not items_error:
            # Normalize items & calculate subtotal first
            normalized_items = []
            subtotal = Decimal('0')

            for raw in items_data:
                kw = (raw.get('product_keyword') or '').strip()
                if not kw:
                    continue

                # quantity
                try:
                    qty = int(raw.get('quantity') or 1)
                    if qty <= 0:
                        qty = 1
                except (TypeError, ValueError):
                    qty = 1

                color = (raw.get('color') or '').strip()

                # amount (per line)
                try:
                    amount = Decimal(str(raw.get('amount') or 0))
                except (TypeError, ValueError, InvalidOperation):
                    amount = Decimal('0')

                subtotal += amount

                normalized_items.append({
                    'product_keyword': kw,
                    'quantity': qty,
                    'color': color,
                    'amount': amount,
                })

            if not normalized_items:
                items_error = "At least one valid product is required."
            else:
                # Create order but not save yet
                order = form.save(commit=False)

                # Delivery area: form theke, na thakle auto-detect
                delivery_area = form.cleaned_data.get('delivery_area')
                valid_values = {c[0] for c in Order.DELIVERY_AREA_CHOICES}
                if delivery_area not in valid_values:
                    delivery_area = detect_delivery_area_from_address(
                        order.address)

                delivery_charge = DELIVERY_CHARGES.get(
                    delivery_area, Decimal('0'))

                order.delivery_area = delivery_area
                order.delivery_charge = delivery_charge
                order.items_subtotal = subtotal

                # Total amount: jodi input na deya hoy, auto calc
                total_amount = form.cleaned_data.get('total_amount')
                if total_amount in (None, ''):
                    total_amount = subtotal + delivery_charge

                order.total_amount = total_amount
                order.save()

                # Create order items
                for item in normalized_items:
                    OrderItem.objects.create(
                        order=order,
                        product_keyword=item['product_keyword'],
                        quantity=item['quantity'],
                        color=item['color'],
                        amount=item['amount'],
                    )

                return redirect('order_success')

    else:
        # GET request → form with default delivery_area
        form = OrderForm(initial={'delivery_area': Order.DELIVERY_AREA_INSIDE})

    # Quick buttons er jonno keywords & colors (admin theke asbe)
    product_keywords = ProductKeyword.objects.filter(is_active=True)
    color_options = ColorOption.objects.filter(is_active=True)

    # Radio button-er selected value handle
    if request.method == 'POST':
        selected_delivery_area = (
            form.data.get('delivery_area')
            or form.initial.get('delivery_area')
            or Order.DELIVERY_AREA_INSIDE
        )
    else:
        selected_delivery_area = form.initial.get(
            'delivery_area',
            Order.DELIVERY_AREA_INSIDE
        )

    context = {
        'form': form,
        'items_error': items_error,
        'items_json': json.dumps(items_data or []),
        'product_keywords': product_keywords,
        'color_options': color_options,
        'selected_delivery_area': selected_delivery_area,
    }
    return render(request, 'orders/order_form.html', context)


def order_success(request):
    return render(request, 'orders/order_success.html')
