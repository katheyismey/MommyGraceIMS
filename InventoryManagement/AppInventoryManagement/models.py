from django.db import models

# Create your models here.
class Post(models.Model):
    # Product ID will be automatically created as the primary key by Django if not explicitly defined.
    name = models.CharField(max_length=200)  # Product Name
    category = models.CharField(max_length=200)  # Product Category
    quantity = models.IntegerField()  # Quantity
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)  # Buying Price
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # Selling Price
    reorder_level = models.IntegerField()  # Reorder Level

    def __str__(self):
        return self.name