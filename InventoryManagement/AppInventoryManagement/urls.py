from django.urls import path
from .views import ProductListView, ProductCreateView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),  # URL for listing products
    path('products/add/', ProductCreateView.as_view(), name='product_add'),  # URL for adding a new product
]
