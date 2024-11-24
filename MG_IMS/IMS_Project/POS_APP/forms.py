from django import forms
from ProductManagement_APP.models import Product, ProductVersion
from .models import TransactionItem

class TransactionItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Select Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    product_version = forms.ModelChoiceField(
        queryset=ProductVersion.objects.none(),  # Populated dynamically via JavaScript
        label="Select Product Version",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'product-version-select'})
    )
    quantity_sold = forms.IntegerField(
        min_value=1,
        label="Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TransactionItem
        fields = ['product', 'product_version', 'quantity_sold']

    def clean(self):
        cleaned_data = super().clean()
        product_version = cleaned_data.get('product_version')
        quantity_sold = cleaned_data.get('quantity_sold')

        if product_version and quantity_sold:
            if product_version.product_quantity < quantity_sold:
                raise forms.ValidationError(
                    f"Not enough stock available for {product_version.product.product_name} (Batch {product_version.batch_id})."
                )
        return cleaned_data
