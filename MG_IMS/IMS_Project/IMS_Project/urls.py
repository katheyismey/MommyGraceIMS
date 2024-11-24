# IMS_Project/urls.py
from django.contrib import admin
from django.urls import path, include
from MGSariSari_Inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('register/', views.register, name='register'),
    path('', views.register, name='home'),  # Root URL directs to the register view
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pos_app/', include('POS_APP.urls')),  # POS_APP URLs
    path('sales/', views.sales_summary, name='sales'),  # Updated to use the sales_summary view
    path('debts/', views.debts, name='debts'),
    path('logout/', views.custom_logout, name='logout'),
    path('sales-summary/', views.sales_summary, name='sales_summary'),
    path('inventory/', include('ProductManagement_APP.urls')),  # Include inventory app's URL patterns
    path('expenses/', include('ExpensesTracker_APP.urls')),  # Project-level route
    
]
