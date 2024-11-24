from django.db import models
from ProductManagement_APP.models import Product, ProductVersion

class Transaction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def calculate_total(self):
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Transaction {self.id} - {self.date}"

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    product_version = models.ForeignKey(ProductVersion, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()

    def get_total_price(self):
        return self.quantity_sold * self.product_version.selling_price

    def save(self, *args, **kwargs):
        if self.quantity_sold > self.product_version.product_quantity:
            raise ValueError(
                f"Not enough stock for {self.product_version.product.product_name} (Batch {self.product_version.batch_id})"
            )

        self.product_version.product_quantity -= self.quantity_sold
        self.product_version.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_version.product.product_name} - {self.quantity_sold} units"
