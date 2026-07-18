import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserRegistrationForm, UserProfileForm
from home.models import Booking, Review as HomeReview
from django.db.models import Q
from catalog.cart import Cart
from catalog.models import Order, OrderItem
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
                
            return redirect('accounts:dashboard')
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
    next_page = 'home:home'  

    def dispatch(self, request, *args, **kwargs):
        # Grab the current cart state before Django clears the session
        current_cart = request.session.get('cart', {})
        
        # Let Django proceed with standard logout session clearing
        response = super().dispatch(request, *args, **kwargs)
        
        # Handle the cookie update accurately
        if current_cart:
            # If they have items, save them for next time
            response.set_cookie('saved_cart', json.dumps(current_cart), max_age=30*24*60*60)
        else:
            # IF THE CART IS EMPTY: Force-delete the cookie so it doesn't add them on next login
            response.delete_cookie('saved_cart')
            
        return response


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/update_profile.html', {'form': form})

@login_required
def dashboard(request):
    # 1. Fetch data from DB
    bookings_query = Booking.objects.filter(user=request.user).order_by('-id')
    reviews_query = HomeReview.objects.filter(user=request.user).order_by('-id')

    context = {
        'user_bookings': bookings_query, 
        'user_reviews': reviews_query,    
        'user_orders': Order.objects.filter(user=request.user).order_by('-id'),
    }
    
    return render(request, 'accounts/dashboard.html', context)