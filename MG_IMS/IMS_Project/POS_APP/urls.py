from django.urls import path, include
from . import views

app_name = 'POS_APP'

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('complete_transaction/', views.complete_transaction, name='complete_transaction'),
    path('search_products/', views.search_products, name='search_products'),
    path('search_batches/', views.search_batches, name='search_batches'),  # New route
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('transaction_records/', views.transaction_records, name='transaction_records'),
    path('transaction_details/<int:transaction_id>/', views.transaction_details, name='transaction_details'),
]
