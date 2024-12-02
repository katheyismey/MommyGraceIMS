from django.urls import path
from . import views

app_name = 'Debt_Management'

urlpatterns = [
    path('create_customer/', views.create_customer, name='create_customer'),
    path('debt_list/', views.debt_list_view, name='debt_list'),
    path('pay_debt/', views.pay_debt, name='pay_debt'),
     path('pay_all_debts/', views.pay_all_debts, name='pay_all_debts'),
]
