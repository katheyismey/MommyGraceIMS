from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Customer
import json

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
