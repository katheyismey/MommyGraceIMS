from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Sum
from POS_APP.models import Transaction, TransactionItem
from ProductManagement_APP.models import Product 
from datetime import datetime
import json
from decimal import Decimal
import decimal


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the error(s) below.")
    else:
        form = UserCreationForm()

    return render(request, 'MGSariSari_Inventory/register.html', {'form': form})

@login_required
def dashboard(request):
    context = {
        'categories': 7,
        'products': 32,
        'sales': 4500.00,
        'top_products': [
            {'name': 'BEV008', 'sales': 180},
            {'name': 'BEV007', 'sales': 320},
            {'name': 'BEV009', 'sales': 400},
            {'name': 'BEV001', 'sales': 120},
            {'name': 'BEV002', 'sales': 720},
        ],
        'product_list': [
            '8 oz Coca Cola', '8 oz Sprite', '8 oz Royal', 
            '1 L Coca Cola', '1 L Sprite', '1 L Royal', 
            '1 L Red Horse', '1 L Emperador', 'Pilsen Grande'
        ],
    }
    return render(request, 'MGSariSari_Inventory/dashboard.html', context)

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def sales_summary(request):
    selected_year = request.GET.get('select_year', datetime.now().year)
    selected_date_str = request.GET.get('selected-date')
    daily_total_sales = 0
    products_sold_today = []
    top_products_labels = []
    top_products_values = []
    monthly_sales = {}
    top_yearly_products_labels = []
    top_yearly_products_values = []

    # Validate the selected year
    try:
        selected_year = int(selected_year)
    except ValueError:
        selected_year = datetime.now().year

    # Daily Sales Summary
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            
            # Filter transactions for the selected date
            daily_transactions = Transaction.objects.filter(date__date=selected_date)
            daily_total_sales = daily_transactions.aggregate(Sum('total_price'))['total_price__sum'] or decimal.Decimal(0)
            
            # Get all transaction items for the selected day
            transaction_items = TransactionItem.objects.filter(transaction__date__date=selected_date)

            # Product-wise summary
            products_summary = {}
            for item in transaction_items:
                product_name = item.product_version.product.product_name  # Access product via product_version
                if product_name in products_summary:
                    products_summary[product_name]['quantity_sold'] += item.quantity_sold
                    products_summary[product_name]['total_price'] += item.get_total_price()
                else:
                    products_summary[product_name] = {
                        'quantity_sold': item.quantity_sold,
                        'total_price': item.get_total_price()
                    }
            
            # Prepare product summary for template
            products_sold_today = [
                {
                    'name': product,
                    'quantity_sold': details['quantity_sold'],
                    'total_price': float(details['total_price'])  # Convert Decimal to float
                }
                for product, details in products_summary.items()
            ]

            # Top 5 Products Sold Today
            sorted_products = sorted(products_summary.items(), key=lambda x: x[1]['quantity_sold'], reverse=True)[:5]
            top_products_labels = [product for product, _ in sorted_products]
            top_products_values = [details['quantity_sold'] for _, details in sorted_products]

        except ValueError as e:
            print("Error:", e)

    # Monthly Sales Summary for the Selected Year
    monthly_transactions = Transaction.objects.filter(date__year=selected_year)
    for transaction in monthly_transactions:
        if transaction.total_price is None:
            continue
        month = transaction.date.strftime("%B")
        if month not in monthly_sales:
            monthly_sales[month] = decimal.Decimal(0)
        monthly_sales[month] += transaction.total_price

    monthly_sales_labels = list(monthly_sales.keys())
    monthly_sales_values = [float(value) for value in monthly_sales.values()]  # Convert Decimal to float

    # Calculate total and average sales for the year
    total_sales = sum(monthly_sales_values)
    average_total_sales = total_sales / 12 if total_sales > 0 else 0

    # Top 5 Products Sold in the Year
    yearly_transaction_items = TransactionItem.objects.filter(transaction__date__year=selected_year)
    yearly_products_summary = {}
    for item in yearly_transaction_items:
        product_name = item.product_version.product.product_name  # Access product via product_version
        if product_name in yearly_products_summary:
            yearly_products_summary[product_name]['quantity_sold'] += item.quantity_sold
        else:
            yearly_products_summary[product_name] = {
                'quantity_sold': item.quantity_sold,
            }

    # Prepare top 5 products for the year
    sorted_yearly_products = sorted(yearly_products_summary.items(), key=lambda x: x[1]['quantity_sold'], reverse=True)[:5]
    top_yearly_products_labels = [product for product, _ in sorted_yearly_products]
    top_yearly_products_values = [details['quantity_sold'] for _, details in sorted_yearly_products]

    # Prepare context for template
    context = {
        'daily_total_sales': float(daily_total_sales),  # Convert Decimal to float
        'average_daily_sales': float(daily_total_sales) / sum(product['quantity_sold'] for product in products_sold_today) if products_sold_today else 0,
        'selected_date': selected_date_str,
        'products_sold_today': products_sold_today,
        'top_products_labels_json': json.dumps(top_products_labels),
        'top_products_values_json': json.dumps(top_products_values),
        'monthly_sales_labels': json.dumps(monthly_sales_labels),
        'monthly_sales_values': json.dumps(monthly_sales_values),
        'total_sales': float(total_sales),  # Convert Decimal to float
        'average_total_sales': float(average_total_sales),  # Convert Decimal to float
        'current_year': selected_year,
        'top_yearly_products_labels_json': json.dumps(top_yearly_products_labels),
        'top_yearly_products_values_json': json.dumps(top_yearly_products_values),
    }

    return render(request, 'MGSariSari_Inventory/sales.html', context)

@login_required
def inventory(request):
    return render(request, 'MGSariSari_Inventory/inventory.html')

@login_required
def transactions(request):
    return render(request, 'MGSariSari_Inventory/transactions.html')

@login_required
def debts(request):
    return render(request, 'MGSariSari_Inventory/debts.html')

@login_required
def expenses(request):
    return render(request, 'MGSariSari_Inventory/expenses.html')

