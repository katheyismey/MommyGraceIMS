from django.contrib import admin
from django.urls import path, include
from MGSariSari_Inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('register/', views.register, name='register'),
    path('', views.register, name='home'),  # Root URL directs to the register view
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('transactions/', views.transactions, name='transactions'),
    path('pos/', include('POS_APP.urls')),
    path('sales/', views.sales_summary, name='sales'),  # Updated to use the sales_summary view
    path('debts/', views.debts, name='debts'),
    path('expenses/', views.expenses, name='expenses'),
    path('logout/', views.custom_logout, name='logout'),
    path('sales-summary/', views.sales_summary, name='sales_summary'),
]
