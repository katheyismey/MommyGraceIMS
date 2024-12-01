from django.db import models
from django.utils import timezone
from decimal import Decimal

# Customer Model
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

# Debt Model
class Debt(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debts')
    transaction = models.OneToOneField('POS_APP.Transaction', on_delete=models.CASCADE, related_name='debt')  # Lazy reference to Transaction
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('Unpaid', 'Unpaid'), ('Partially Paid', 'Partially Paid'), ('Paid', 'Paid')],
        default='Unpaid'
    )

    def remaining_balance(self):
        return self.amount_due - self.amount_paid

    def mark_as_paid(self):
        """Mark the debt as fully paid."""
        self.status = 'Paid'
        self.save()

    def __str__(self):
        return f"Debt for {self.customer.get_full_name()} - Amount Due: ₱{self.amount_due} - Status: {self.status}"


