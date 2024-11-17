from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('complete_transaction/', views.complete_transaction, name='complete_transaction'),
    path('search_products/', views.search_products, name='search_products'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),  # New route
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('transactions/', views.pos, name='transactions'),
]
