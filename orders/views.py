import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .forms import OrderForm
from .models import Order, OrderItem


@require_http_methods(["GET", "POST"])
def new_order(request):
    items_error = None
    items_json = "[]"

    if request.method == 'POST':
        items_json = request.POST.get('items_json', '[]').strip() or '[]'

        try:
            items_data = json.loads(items_json)
        except json.JSONDecodeError:
            items_data = []
            items_error = "Product list invalid. Please try again."

        if not items_data:
            items_error = "At least one product is required."

        form = OrderForm(request.POST)

        if form.is_valid() and not items_error:
            order = form.save()

            for item in items_data:
                # item = {'product_keyword': ..., 'quantity': ..., 'color': ..., 'amount': ...}
                kw = item.get('product_keyword', '').strip()
                if not kw:
                    continue  # skip empty row

                try:
                    qty = int(item.get('quantity', 1))
                    if qty <= 0:
                        qty = 1
                except (TypeError, ValueError):
                    qty = 1

                try:
                    amount = float(item.get('amount', 0))
                except (TypeError, ValueError):
                    amount = 0

                color = item.get('color', '').strip()

                OrderItem.objects.create(
                    order=order,
                    product_keyword=kw,
                    quantity=qty,
                    color=color,
                    amount=amount,
                )

            return redirect('order_success')

    else:
        form = OrderForm()

    context = {
        'form': form,
        'items_error': items_error,
        'items_json': items_json,
    }
    return render(request, 'orders/order_form.html', context)


def order_success(request):
    return render(request, 'orders/order_success.html')
