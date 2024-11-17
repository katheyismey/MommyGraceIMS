from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Sum
from .models import Transaction
from datetime import datetime

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

    # Validate the selected year
    try:
        selected_year = int(selected_year)
    except ValueError:
        selected_year = datetime.now().year

    # Monthly summary for the selected year
    monthly_transactions = Transaction.objects.filter(date__year=selected_year)
    monthly_sales = {}

    for transaction in monthly_transactions:
        if transaction.total_price is None:
            continue

        month = transaction.date.strftime("%B")
        if month not in monthly_sales:
            monthly_sales[month] = 0

        monthly_sales[month] += transaction.total_price

    # Prepare data for Chart.js
    monthly_sales_labels = list(monthly_sales.keys())
    monthly_sales_values = list(monthly_sales.values())

    # Calculate total and average sales for the year
    total_sales = sum(monthly_sales_values)
    average_total_sales = total_sales / 12 if total_sales > 0 else 0

    # Daily sales summary
    selected_date_str = request.GET.get('selected-date')
    daily_total_sales = 0

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            daily_transactions = Transaction.objects.filter(date__date=selected_date)
            daily_total_sales = daily_transactions.aggregate(Sum('total_price'))['total_price__sum'] or 0
        except ValueError:
            pass

    # Prepare the context for the template
    context = {
        'monthly_sales': monthly_sales,
        'monthly_sales_labels': monthly_sales_labels,
        'monthly_sales_values': monthly_sales_values,
        'total_sales': total_sales,
        'average_total_sales': average_total_sales,
        'current_year': selected_year,
        'daily_total_sales': daily_total_sales,
        'average_daily_sales': 0,  # Update this if you need daily average logic
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
