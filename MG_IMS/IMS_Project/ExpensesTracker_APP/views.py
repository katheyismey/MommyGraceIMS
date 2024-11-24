from django.shortcuts import render
from ExpensesTracker_APP.models import ExpenseLog
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate

def expenses_tracker(request):
    # Get filter parameters
    search_query = request.GET.get('q', '')  # Search keyword
    start_date = request.GET.get('start_date', '')  # Start date
    end_date = request.GET.get('end_date', '')  # End date

    # Filter expense logs
    expense_logs = ExpenseLog.objects.all()

    # Apply search filter if there's a query
    if search_query:
        expense_logs = expense_logs.filter(
            Q(product_version__product__product_name__icontains=search_query)
        )
    
    # Apply date filters if both are provided
    if start_date and end_date:
        expense_logs = expense_logs.filter(date_added__range=[start_date, end_date])
    # Apply start_date filter only
    elif start_date:
        expense_logs = expense_logs.filter(date_added__gte=start_date)
    # Apply end_date filter only
    elif end_date:
        expense_logs = expense_logs.filter(date_added__lte=end_date)
        
    # Sort the logs by date_added in descending order (most recent at the top)
    expense_logs = expense_logs.order_by('-date_added')

    # Aggregate daily expenses (by date)
    daily_expenses = expense_logs.annotate(date_only=TruncDate('date_added')) \
        .values('date_only') \
        .annotate(total_cost=Sum('total_cost')) \
        .order_by('date_only')

    # Prepare data for the line graph
    labels = [entry['date_only'].strftime('%Y-%m-%d') for entry in daily_expenses]  # Format dates for chart
    expenses = [float(entry['total_cost']) for entry in daily_expenses]  # Convert Decimal to float

    # Calculate total expense for the filtered results
    total_expense = expense_logs.aggregate(total_cost=Sum('total_cost'))['total_cost'] or 0

    return render(request, 'ExpensesTracker_APP/expenses_tracker.html', {
        'expense_logs': expense_logs,
        'total_expense': total_expense,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'labels': labels,
        'expenses': expenses,
    })
