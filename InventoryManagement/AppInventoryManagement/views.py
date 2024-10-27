from django.shortcuts import render

from django.views.generic import ListView, CreateView
from .models import Post
from django.urls import reverse_lazy
from django.http import HttpResponse

# Create your views here.
class ProductListView(ListView):
    model = Post
    template_name = 'AppInventoryManagement/product_list.html'  # Customize the template path
    context_object_name = 'products'  # Name used in template to access product list

# Product Create View: Allow users to add a new product
class ProductCreateView(CreateView):
    model = Post
    template_name = 'AppInventoryManagement/product_form.html'  # Customize the template path
    fields = ['name', 'category', 'quantity', 'buying_price', 'selling_price', 'reorder_level'] 
    success_url = reverse_lazy('product_list')  # Redirect to product list view after creation
    
def home(request):
    return HttpResponse("Welcome to the Inventory Management System")