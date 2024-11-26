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
    transaction_id = models.CharField(max_length=50, unique=True)  # Can be linked to a transaction ID
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

# Payment Model
class Payment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of ₱{self.amount_paid} for Debt {self.debt.id} on {self.date_paid}"

    def save(self, *args, **kwargs):
        """Override save method to update the debt status if fully paid."""
        super().save(*args, **kwargs)
        # Update the debt's amount_paid and check if it's fully paid
        self.debt.amount_paid += self.amount_paid
        if self.debt.amount_paid >= self.debt.amount_due:
            self.debt.mark_as_paid()  # Mark the debt as 'Paid' when it's fully paid
        self.debt.save()
