# inventory/urls.py

from django.urls import path
from . import views

app_name = 'ProductManagement_APP'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    path('add_category/', views.add_category, name='add_category'), 
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    
    path('stock_in/<int:version_id>/', views.stock_in, name='stock_in'),
    path('stock_out/<int:version_id>/', views.stock_out, name='stock_out'),
    
     # New routes for ProductVersion management
    path('add_product_version/<int:product_id>/', views.add_product_version, name='add_product_version'),
    path('edit_product_version/<int:version_id>/', views.edit_product_version, name='edit_product_version'),
    path('delete_product_version/<int:version_id>/', views.delete_product_version, name='delete_product_version'),

    # New routes for Supplier management
    path('add_supplier/', views.add_supplier, name='add_supplier'),
    path('edit_supplier/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
]