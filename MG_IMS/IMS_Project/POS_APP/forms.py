# POS_APP/forms.py
from django import forms # type: ignore
from .models import TransactionItem, Product

class TransactionItemForm(forms.ModelForm):
    class Meta:
        model = TransactionItem
        fields = ['product', 'quantity_sold']

    def clean_quantity_sold(self):
        quantity_sold = self.cleaned_data['quantity_sold']
        product = self.cleaned_data.get('product')
        
        # Ensure there's enough stock
        if product and quantity_sold > product.quantity:
            raise forms.ValidationError(f"Only {product.quantity} items available in stock.")
        
        return quantity_sold
