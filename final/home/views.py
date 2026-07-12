from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from catalog.models import Item, Review
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Booking
from datetime import datetime
from django.db.models import Q

def home(request):
    return render (request, 'home/index.html', {})
def tasks(request):
    return render (request, 'home/tasks.html', {})
def contact(request):
    return render (request, 'home/contact.html', {})
def about(request):
    return render (request, 'home/about.html', {})
def reviews(request):
    return render (request, 'home/reviews.html', {})

@login_required
@require_POST
def add_review_ajax(request):
    try:
        item_id = request.POST.get('item_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not all([item_id, rating, comment]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Selected catalog item does not exist.'}, status=404)

        rating_val = int(rating)
        if not (1 <= rating_val <= 5):
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'}, status=400)

        review = Review.objects.create(
            item=item,
            user=request.user,
            rating=rating_val,
            comment=comment
        )

        return JsonResponse({
            'success': True,
            'username': request.user.username,
            'item_title': item.title,
            'rating': review.rating,
            'comment': review.comment,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def book_appointment(request):
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        notes = request.POST.get('notes', '')
        Booking.objects.create(
            user=request.user,
            service_type=service_type,
            notes=notes
        )
    
        return redirect('dashboard')
        
    return redirect('home')

@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
    return redirect('dashboard')

from django.http import JsonResponse
from datetime import datetime
from .models import Booking

def check_taken_slots(request):
    date_str = request.GET.get('date')
    artist_str = request.GET.get('artist')
    
    if not date_str or not artist_str:
        return JsonResponse({'taken_slots': []})
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        month_name = date_obj.strftime("%B")
        day_num = str(int(date_obj.strftime("%d")))
        year_num = date_obj.strftime("%Y")
        
        formatted_date_string = f"{month_name} {day_num}, {year_num}"
    except ValueError:
        return JsonResponse({'taken_slots': []})

    existing_bookings = Booking.objects.filter(
        Q(notes__icontains=f"Artist: {artist_str}") & 
        Q(notes__icontains=f"Date: {formatted_date_string}")
    )

    taken_slots = []
    for booking in existing_bookings:
        if " @ " in booking.notes:
            try:
                time_part = booking.notes.split(" @ ")[1].strip()
                time_obj = datetime.strptime(time_part, "%I:%M %p")
                military_time = time_obj.strftime("%H:%M")
                taken_slots.append(military_time)
            except (ValueError, IndexError):
                continue

    return JsonResponse({'taken_slots': taken_slots})