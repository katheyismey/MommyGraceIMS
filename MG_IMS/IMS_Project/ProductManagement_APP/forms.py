# inventory/forms.py

from django import forms # type: ignore
from .models import Product, Category, ProductVersion, Supplier

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_classification', 'reorder_level', 'category']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'contact_details']

    # Optional: You can add validation for supplier details if necessary
    def clean_supplier_name(self):
        supplier_name = self.cleaned_data.get('supplier_name')
        if Supplier.objects.filter(supplier_name=supplier_name).exists():
            raise forms.ValidationError("Supplier with this name already exists.")
        return supplier_name

class ProductVersionForm(forms.ModelForm):
    # This form will handle the addition or editing of a product version (specific to a supplier, price, and stock)
    class Meta:
        model = ProductVersion
        fields = ['product', 'supplier', 'buying_price', 'product_quantity', 'selling_price', 'batch_id']

    # You can also add custom logic for handling price validation if needed:
    def clean_buying_price(self):
        price = self.cleaned_data.get('buying_price')
        if price <= 0:
            raise forms.ValidationError("Buying price must be greater than zero.")
        return price

    def clean_selling_price(self):
        price = self.cleaned_data.get('selling_price')
        if price <= 0:
            raise forms.ValidationError("Selling price must be greater than zero.")
        return price