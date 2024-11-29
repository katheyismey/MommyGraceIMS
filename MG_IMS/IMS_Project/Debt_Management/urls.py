from django.urls import path
from . import views

app_name = 'Debt_Management'

urlpatterns = [
    path('create_customer/', views.create_customer, name='create_customer'),
]
