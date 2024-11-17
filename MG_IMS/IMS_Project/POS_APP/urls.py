from django.urls import path # type: ignore
from . import views

app_name = 'POS_APP'

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),  # http://127.0.0.1:8000/pos_app/pos/
    path('complete_transaction/', views.complete_transaction, name='complete_transaction'),
    path('search_products/', views.search_products, name='search_products'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
]
