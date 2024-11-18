# POS_APP/views.py
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib import messages # type: ignore
from django.http import JsonResponse # type: ignore
from .models import Transaction, TransactionItem, Product
from .forms import TransactionItemForm
from django.views.decorators.http import require_POST # type: ignore
from django.middleware.csrf import get_token # type: ignore
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage # type: ignore
import json

# GET Product to Transaction
def pos_view(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity_sold') or 1)

        if product_id and quantity:
            product = get_object_or_404(Product, id=product_id)
            cart = request.session.get('cart', [])

            # Check if the product is already in the cart
            existing_item = next((item for item in cart if item['product_id'] == product.id), None)
            if existing_item:
                existing_item['quantity'] += quantity
            else:
                cart.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'price': float(product.selling_price),
                })

            request.session['cart'] = cart  # Save cart back to session
            messages.success(request, f"Added {quantity} of {product.name} to the cart.")
            return redirect('POS_APP:pos')
        else:
            messages.error(request, "Please select a product and enter a quantity.")

    form = TransactionItemForm()
    cart = request.session.get('cart', [])
    total = sum(item['quantity'] * item['price'] for item in cart)

    return render(request, "pos/pos.html", {"form": form, "cart": cart, "total": total})


def complete_transaction(request):
    cart = request.session.get('cart', [])
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('POS_APP:pos')

    # Create a new transaction and add items
    transaction = Transaction.objects.create()
    for item in cart:
        product = Product.objects.get(id=item['product_id'])
        TransactionItem.objects.create(transaction=transaction, product=product, quantity_sold=item['quantity'])

    # Calculate the total and save it to the transaction
    transaction.calculate_total()
    
    # Clear the cart
    request.session['cart'] = []
    messages.success(request, "Transaction completed successfully.")
    return redirect('POS_APP:pos')

def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)[:10]  # Limit results to 10
    else:
        products = Product.objects.all()[:10]  # Show the first 10 products by default

    results = [
        {
            "id": product.id,
            "name": product.name,
            "selling_price": product.selling_price,
        }
        for product in products
    ]

    return JsonResponse(results, safe=False)

@require_POST
def update_cart_item(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if product_id and quantity is not None:
        cart = request.session.get('cart', [])
        for item in cart:
            if item['product_id'] == int(product_id):
                item['quantity'] = quantity
                break
        request.session['cart'] = cart
        return JsonResponse({"success": True, "updated_quantity": quantity})
    return JsonResponse({"success": False})

@require_POST
def remove_from_cart(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')

    cart = request.session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != int(product_id)]
    request.session['cart'] = cart
    return JsonResponse({"success": True})

@require_POST
def clear_cart(request):
    request.session['cart'] = []
    return JsonResponse({"success": True})

def transaction_records(request):
    query = request.GET.get('query', '')  # Get the search query from the URL
    transactions_list = Transaction.objects.prefetch_related('items__product').order_by('id')

    if query.isdigit():  # Check if the query is a digit
        transactions_list = transactions_list.filter(id=query)  # Exact match for transaction ID
    elif query:  # If the query is not numeric, return an empty queryset
        transactions_list = transactions_list.none()

    paginator = Paginator(transactions_list, 9)  # 9 transactions per page
    page = request.GET.get('page', 1)

    try:
        transactions = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        transactions = paginator.page(1)  # Default to first page if invalid page

    return render(request, 'pos/transaction_records.html', {
        'transactions': transactions,
        'query': query  # Pass the query to the template
    })
