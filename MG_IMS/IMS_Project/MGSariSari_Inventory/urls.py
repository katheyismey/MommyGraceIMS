from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages


def register(request):
    # Redirect authenticated users directly to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to the dashboard if logged in

    # Handle registration for new users
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')  # Redirect to login page after registration
        else:
            messages.error(request, "Registration failed. Please correct the error(s) below.")
    else:
        form = UserCreationForm()

    return render(request, 'MGSariSari_Inventory/register.html', {'form': form})

