from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Customer, Debt
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q

@csrf_exempt
def create_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone = data.get("phone", "")

            if not first_name or not last_name:
                return JsonResponse({"success": False, "error": "First and last name are required."}, status=400)

            customer = Customer.objects.create(first_name=first_name, last_name=last_name, phone=phone)

            return JsonResponse({
                "success": True,
                "customer": {
                    "id": customer.id,
                    "full_name": customer.get_full_name(),
                },
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

@csrf_exempt
@transaction.atomic
def pay_debt(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            debt_id = data.get("debt_id")
            amount = Decimal(data.get("amount", "0"))

            debt = get_object_or_404(Debt, id=debt_id)

            if amount <= 0:
                return JsonResponse({"success": False, "error": "Amount must be greater than 0."})

            if debt.remaining_balance() < amount:
                return JsonResponse({"success": False, "error": "Amount exceeds remaining balance."})

            # Lock the row to avoid concurrency issues
            debt.amount_paid += amount
            if debt.remaining_balance() <= 0:
                debt.mark_as_paid()
            debt.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})

def debt_list_view(request):
    query = request.GET.get('query', '').strip()  # Get the search query and remove extra whitespace
    debts = Debt.objects.select_related('customer', 'transaction').all()

    if query:  # If a search query is provided, filter debts by customer name
        # Split the query into parts for first and last name
        query_parts = query.split()
        if len(query_parts) == 1:  # Single name provided
            debts = debts.filter(
                Q(customer__first_name__icontains=query_parts[0]) |
                Q(customer__last_name__icontains=query_parts[0])
            )
        elif len(query_parts) > 1:  # Full name provided
            debts = debts.filter(
                Q(customer__first_name__icontains=query_parts[0]) &
                Q(customer__last_name__icontains=" ".join(query_parts[1:]))
            )

    # Separate unpaid and paid debts
    unpaid_debts = debts.filter(status__in=['Unpaid', 'Partially Paid'])
    paid_debts = debts.filter(status='Paid')

    # Combine unpaid and paid debts (paid debts come last)
    all_debts = list(unpaid_debts) + list(paid_debts)

    # Paginate debts
    paginator = Paginator(all_debts, 10)  # Show 10 rows per page
    page_number = request.GET.get('page', 1)
    debts_page = paginator.get_page(page_number)

    return render(request, 'debt_management/debt_list.html', {'debts': debts_page, 'query': query})