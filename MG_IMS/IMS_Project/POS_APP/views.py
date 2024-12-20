from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from ProductManagement_APP.models import Product, ProductVersion
from .models import Transaction, TransactionItem
from Debt_Management.models import Customer  # Import Customer model
from Debt_Management.models import Debt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# GET Products and Product Versions for Transactions
# Add to Cart in pos_view
def pos_view(request):
    if request.method == "POST":
        product_version_id = request.POST.get('product_version_id')
        quantity = int(request.POST.get('quantity_sold') or 1)

        if product_version_id and quantity:
            product_version = get_object_or_404(ProductVersion, id=product_version_id)
            
            # Check stock availability
            if quantity > product_version.product_quantity:
                messages.error(request, f"Not enough stock for {product_version.product.product_name} (Batch: {product_version.batch_id}). Available: {product_version.product_quantity}.")
                return redirect('POS_APP:pos')

            cart = request.session.get('cart', [])
            
            # Check if the product version is already in the cart
            existing_item = next((item for item in cart if item['product_version_id'] == product_version.id), None)
            if existing_item:
                if existing_item['quantity'] + quantity > product_version.product_quantity:
                    messages.error(request, f"Cannot add more than {product_version.product_quantity} items for {product_version.product.product_name} (Batch: {product_version.batch_id}).")
                    return redirect('POS_APP:pos')
                existing_item['quantity'] += quantity
            else:
                cart.append({
                    'product_version_id': product_version.id,
                    'product_name': product_version.product.product_name,
                    'batch_id': product_version.batch_id,
                    'quantity': quantity,
                    'price': float(product_version.selling_price),
                })

            request.session['cart'] = cart  # Save cart back to session
            messages.success(request, f"Added {quantity} of {product_version.product.product_name} (Batch: {product_version.batch_id}) to the cart.")
            return redirect('POS_APP:pos')
        else:
            messages.error(request, "Please select a product version and enter a quantity.")

    cart = request.session.get('cart', [])
    total = sum(item['quantity'] * item['price'] for item in cart)
    customers = Customer.objects.all()  # Pass customers for "Pay Later"

    return render(request, "pos/pos.html", {"cart": cart, "total": total, "customers": customers})

def complete_transaction(request):
    cart = request.session.get('cart', [])
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('POS_APP:pos')

    status = request.POST.get('status', 'Paid')
    customer_id = request.POST.get('customer_id')

    customer = None
    if status == 'Pay Later':
        # Validate customer
        if not customer_id:
            messages.error(request, "Customer must be selected for 'Pay Later' transactions.")
            return redirect('POS_APP:pos')
        customer = get_object_or_404(Customer, id=customer_id)

    # Create a new transaction
    transaction = Transaction.objects.create(status=status, customer=customer)

    for item in cart:
        product_version = ProductVersion.objects.get(id=item['product_version_id'])
        TransactionItem.objects.create(transaction=transaction, product_version=product_version, quantity_sold=item['quantity'])

    # Calculate the total and save it to the transaction
    transaction.calculate_total()

    # If the transaction is marked as "Pay Later," create a Debt record
    if status == 'Pay Later' and customer:
        from datetime import date, timedelta

        Debt.objects.create(
            customer=customer,
            transaction=transaction,
            amount_due=transaction.total_price,
            amount_paid=0,  # Initially no payment is made
            due_date=date.today() + timedelta(days=30),  # Example: 30 days from today
            status='Unpaid'  # Default status
        )

    # Clear the cart
    request.session['cart'] = []
    messages.success(request, "Transaction completed successfully.")
    return redirect('POS_APP:pos')


def search_products(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)[:10]  # Limit to 10 results
    else:
        products = Product.objects.all()[:10]

    results = [
        {
            "id": product.product_id,
            "name": product.product_name,
            "total_quantity": product.total_quantity,
        }
        for product in products
    ]
    return JsonResponse(results, safe=False)

def search_batches(request):
    product_id = request.GET.get('product_id', '')
    if product_id:
        product_versions = ProductVersion.objects.filter(product_id=product_id, product_quantity__gt=0)
    else:
        product_versions = ProductVersion.objects.none()

    results = [
        {
            "id": version.id,
            "batch_id": version.batch_id,
            "price": float(version.selling_price),
            "stock": version.product_quantity,
        }
        for version in product_versions
    ]
    return JsonResponse(results, safe=False)

@require_POST
def update_cart_item(request):
    data = json.loads(request.body)
    product_version_id = data.get('product_version_id')
    quantity = data.get('quantity')

    if product_version_id and quantity is not None:
        product_version = get_object_or_404(ProductVersion, id=product_version_id)

        # Validate against available stock
        if quantity > product_version.product_quantity:
            return JsonResponse({
                "success": False,
                "error": f"Cannot exceed stock of {product_version.product_quantity} for this product."
            })

        cart = request.session.get('cart', [])
        for item in cart:
            if item['product_version_id'] == int(product_version_id):
                item['quantity'] = quantity
                break
        request.session['cart'] = cart
        return JsonResponse({"success": True, "updated_quantity": quantity})
    return JsonResponse({"success": False})

@require_POST
def remove_from_cart(request):
    data = json.loads(request.body)
    product_version_id = data.get('product_version_id')

    cart = request.session.get('cart', [])
    cart = [item for item in cart if item['product_version_id'] != int(product_version_id)]
    request.session['cart'] = cart
    return JsonResponse({"success": True})

@require_POST
def clear_cart(request):
    request.session['cart'] = []
    return JsonResponse({"success": True})

def transaction_records(request):
    query = request.GET.get('query', '')
    transactions_list = Transaction.objects.prefetch_related('items__product_version__product').annotate(
        total_items=Sum('items__quantity_sold')  # Annotate total items
    ).order_by('id')

    if query.isdigit():
        transactions_list = transactions_list.filter(id=query)
    elif query:
        transactions_list = transactions_list.none()

    paginator = Paginator(transactions_list, 10)
    page = request.GET.get('page', 1)

    try:
        transactions = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        transactions = paginator.page(1)

    return render(request, 'pos/transaction_records.html', {
        'transactions': transactions,
        'query': query
    })

def transaction_details(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    items = [
        {
            "product_name": item.product_version.product.product_name,
            "quantity_sold": item.quantity_sold,
            "selling_price": float(item.product_version.selling_price)
        }
        for item in transaction.items.all()
    ]
    data = {
        "id": transaction.id,
        "date": transaction.date.strftime("%Y-%m-%d %H:%M"),
        "total_price": float(transaction.total_price),
        "items": items,
        "customer": transaction.customer.get_full_name() if transaction.customer else None,
        "status": transaction.status
    }
    return JsonResponse(data)