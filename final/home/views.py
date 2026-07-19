from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Booking, Service, Review
from datetime import datetime
from django.db.models import Q

def home(request):
    return render(request, 'home/index.html', {})

def tasks(request):
    # retrieves all services from the databse
    db_services = Service.objects.all()
    return render(request, 'home/tasks.html', {
        'piercing_services': db_services
    })

def contact(request):
    return render(request, 'home/contact.html', {})

def about(request):
    return render(request, 'home/about.html', {})


def reviews(request):
    all_reviews = Review.objects.all().order_by('-id')
    db_services = Service.objects.all()
    return render(request, 'home/reviews.html', {
        'reviews': all_reviews,
        'services': db_services
    })

@login_required
@require_POST
def add_review_ajax(request):
    try:
        # collects review data
        service_id = request.POST.get('item_id') or request.POST.get('service_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        # checks to make sure that none of these three values are empty or missing
        if not all([service_id, rating, comment]):
            return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)
        # service id validation
        try:
            service_obj = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Selected service item does not exist.'}, status=404)
        # rating validation
        try:
            rating_val = int(rating)
            if not (1 <= rating_val <= 5):
                raise ValueError()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'}, status=400)
        # review is saved to database
        review = Review.objects.create(
            service=service_obj,
            user=request.user,
            rating=rating_val,
            comment=comment
        )

        return JsonResponse({
            'success': True,
            'username': request.user.username,
            'item_title': service_obj.title,
            'rating': review.rating,
            'comment': review.comment,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        artist = request.POST.get('artist')
        notes = request.POST.get('notes', '')

        selected_service = get_object_or_404(Service, id=service_id)

        Booking.objects.create(
            user=request.user,
            service=selected_service,
            artist=artist,
            notes=notes
        )
        return redirect('accounts:dashboard')

@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
    return redirect('accounts:dashboard')

def check_taken_slots(request):
    date_str = request.GET.get('date')
    artist_str = request.GET.get('artist')
    # if date or artist is missig return an empoty array
    if not date_str or not artist_str:
        return JsonResponse({'taken_slots': []})
    # make the text match
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        month_name = date_obj.strftime("%B")
        day_num = str(int(date_obj.strftime("%d")))
        year_num = date_obj.strftime("%Y")
        
        formatted_date_string = f"{month_name} {day_num}, {year_num}"
    except ValueError:
        return JsonResponse({'taken_slots': []})
    # Q is used to form database queries, AND in this case
    existing_bookings = Booking.objects.filter(
        #case insensitive lookup in notes which is artist and date, returns existing bookings for that artist on that date
        Q(notes__icontains=f"Artist: {artist_str}") & 
        Q(notes__icontains=f"Date: {formatted_date_string}")
    )

    taken_slots = []
    for booking in existing_bookings:
        if " @ " in booking.notes:
            # split the @ (timeslot) PM from the date
            try:
                time_part = booking.notes.split(" @ ")[1].strip()
                time_obj = datetime.strptime(time_part, "%I:%M %p")
                military_time = time_obj.strftime("%H:%M")
                # taken slots are appended
                taken_slots.append(military_time)
            except (ValueError, IndexError):
                continue

    return JsonResponse({'taken_slots': taken_slots})