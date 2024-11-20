# inventory/models.py
from django.db import models
from django.db.models import Sum

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255, unique=True)
    product_classification = models.CharField(max_length=100)
    reorder_level = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    @property
    def total_quantity(self):
        # Calculate the total quantity by summing related product versions' quantities
        return self.versions.aggregate(total=Sum('product_quantity'))['total'] or 0

    def __str__(self):
        return self.product_name

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255, unique=True)
    contact_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.supplier_name

class ProductVersion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='versions')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField()  # This tracks stock quantity for each product version
    batch_id = models.CharField(max_length=50)  # Unique batch ID for FIFO tracking
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp for FIFO logic

    def __str__(self):
        return f"{self.product.product_name} - {self.supplier.supplier_name} ({self.batch_id})"

    class Meta:
        ordering = ['date_added']  # FIFO: First in first out logic based on the `date_added`

class StockLog(models.Model):
    ACTION_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]

    product_version = models.ForeignKey(ProductVersion, on_delete=models.CASCADE, related_name='stock_logs')
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product_version} - {self.action_type} ({self.quantity})"
