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
    # cart triggered registration
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # save the guests cart so their items are still there after signing up
            temp_cart = request.session.get('cart', None)
            # the user isnt saved just yet
            user = form.save(commit=False)
            # password is hashed
            user.set_password(form.cleaned_data['password'])
            # now it saved
            user.save()
            
            login(request, user)
            # guest cart is appended to the new account (if there are items stored)
            if temp_cart is not None:
                request.session['cart'] = temp_cart
                request.session.modified = True
                
            return redirect('accounts:dashboard')
    # by clicking register here
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        # on login cart is loaded
        saved_cart_cookie = self.request.COOKIES.get('saved_cart')
        response = super().form_valid(form)
        if saved_cart_cookie:
            try:
                self.request.session['cart'] = json.loads(saved_cart_cookie)
                self.request.session.modified = True
            # if the cookie is corrupted it logs the user in instead of crashing the page
            except json.JSONDecodeError:
                pass
                
        return response

class CustomLogoutView(LogoutView):
    next_page = 'home:home'  

    def dispatch(self, request, *args, **kwargs):
        # grab the current cart state before django clears the session
        current_cart = request.session.get('cart', {})
        
        # logout session clearing
        response = super().dispatch(request, *args, **kwargs)
        
        # handles cookie update accurately
        if current_cart:
            # if they have items, save them for next time
            response.set_cookie('saved_cart', json.dumps(current_cart), max_age=30*24*60*60)
        else:
            # if cart is empty delete the cookie
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
    # fetch data from db
    bookings_query = Booking.objects.filter(user=request.user).order_by('-id')
    reviews_query = HomeReview.objects.filter(user=request.user).order_by('-id')

    context = {
        'user_bookings': bookings_query, 
        'user_reviews': reviews_query,    
        'user_orders': Order.objects.filter(user=request.user).order_by('-id'),
    }
    
    return render(request, 'accounts/dashboard.html', context)