from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def calculate_total(self):
        # Calculate the total price of all items in this transaction
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Transaction {self.id} - {self.date}"

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()

    def get_total_price(self):
        return self.quantity_sold * self.product.selling_price

    def save(self, *args, **kwargs):
        # Deduct the quantity from the product's stock
        if self.quantity_sold > self.product.quantity:
            raise ValueError(f"Not enough stock for {self.product.name}")

        self.product.quantity -= self.quantity_sold
        self.product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold} units"
