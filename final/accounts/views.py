import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegistrationForm, UserProfileForm
from catalog.models import Review
from home.models import Booking
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            temp_cart = request.session.get('cart', None)
            
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            login(request, user)
            
            if temp_cart is not None:
                request.session['cart'] = temp_cart
                request.session.modified = True
                
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        saved_cart_cookie = self.request.COOKIES.get('saved_cart')
        response = super().form_valid(form)
        if saved_cart_cookie:
            try:
                self.request.session['cart'] = json.loads(saved_cart_cookie)
                self.request.session.modified = True
            except json.JSONDecodeError:
                pass
                
        return response

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        current_cart = request.session.get('cart', None)
        response = super().dispatch(request, *args, **kwargs)
        if current_cart:
            response.set_cookie('saved_cart', json.dumps(current_cart), max_age=30*24*60*60)
            
        return response

@login_required
def dashboard(request):
    # Pull user reviews from catalog.models
    user_reviews = Review.objects.filter(user=request.user).select_related('item').order_by('-created_at')
    
    # Pull user bookings from catalog.models 
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'user_reviews': user_reviews,
        'user_bookings': user_bookings,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/update_profile.html', {'form': form})

@login_required
def dashboard(request):
    user_reviews = Review.objects.filter(user=request.user).select_related('item').order_by('-created_at')
    
    user_bookings = Booking.objects.filter(user=request.user).order_by('-id')
    
    context = {
        'user_reviews': user_reviews,
        'user_bookings': user_bookings,
    }
    return render(request, 'accounts/dashboard.html', context)