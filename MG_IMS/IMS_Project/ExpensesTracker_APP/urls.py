from django.urls import path
from .views import expenses_tracker

app_name = 'ExpensesTracker_APP'

urlpatterns = [
    path('', expenses_tracker, name='expenses_tracker'),  # App-level route
]