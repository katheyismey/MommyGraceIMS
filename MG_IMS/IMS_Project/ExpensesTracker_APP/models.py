from django.db import models
from ProductManagement_APP.models import ProductVersion

class ExpenseLog(models.Model):
    product_version = models.ForeignKey(ProductVersion, on_delete=models.CASCADE, related_name='expense_logs')
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Expense for {self.product_version} on {self.date_added}"
