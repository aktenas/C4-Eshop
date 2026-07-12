from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/', views.tasks, name='tasks'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/', views.reviews, name='reviews'), 
    path('reviews/add/ajax/', views.add_review_ajax, name='add_review_ajax'),
    path('book/confirm/', views.book_appointment, name='book_appointment'),
    path('book/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('book/check-slots/', views.check_taken_slots, name='check_taken_slots'),
]