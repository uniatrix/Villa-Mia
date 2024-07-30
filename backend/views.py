from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views import View
from .forms import RoomForm, RoomCategoryForm, BookingForm, NewsletterEmailForm
from .models import Room, Booking, Category, NewsletterEmail
import datetime

# Index view to handle home page and booking form submission
def index(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.save()
            return redirect('success_page')
    else:
        form = BookingForm()
    return render(request, "backend/index.html", {'form': form})

# View to display categories
def room_view(request):
    categories = Category.objects.all()
    return render(request, 'backend/room_view.html', {'categories': categories})

# View to display rooms based on selected category
def category_rooms(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    rooms = Room.objects.filter(category=category)
    if request.method == 'POST':
        form = RoomCategoryForm(request.POST)
        if form.is_valid():
            room_id = request.POST.get('room_id')
            room = Room.objects.get(id=room_id)
            room.category = form.cleaned_data['category']
            room.available = form.cleaned_data['available']
            room.save()
            return redirect('category_rooms', category_id=category.id)
    else:
        form = RoomCategoryForm()
    return render(request, 'backend/category_rooms.html', {'category': category, 'rooms': rooms, 'form': form})

# View to handle adding new rooms by staff
@user_passes_test(lambda u: u.is_staff)
def add_room_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('room_view')
    else:
        form = RoomForm()
    return render(request, 'backend/add_room.html', {'form': form})

# AJAX view to load rooms based on category selection
def load_rooms(request):
    category_id = request.GET.get('category_id')
    rooms = Room.objects.filter(category_id=category_id).order_by('title')
    return JsonResponse(list(rooms.values('id', 'title')), safe=False)

# Admin view to manage bookings and confirm them
@user_passes_test(lambda u: u.is_staff)
def admin_bookings(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.room.available = False
        booking.room.save()
        booking.confirmed = True
        booking.save()
        return redirect('admin_bookings')

    bookings = Booking.objects.all()
    return render(request, 'backend/admin_bookings.html', {'bookings': bookings})

# View to check room availability and handle booking form submission
def check_availability(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    bookings = Booking.objects.filter(room=room).exclude(check_out__lt=datetime.date.today())
    
    booked_dates = []
    for booking in bookings:
        current_date = booking.check_in
        while current_date <= booking.check_out:
            booked_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            booking.save()
            return redirect('success_page')
    else:
        form = BookingForm()
    
    return render(request, 'backend/check_availability.html', {
        'room': room, 
        'booked_dates': booked_dates, 
        'form': form
    })

# View to delete a booking
@user_passes_test(lambda u: u.is_staff)
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('admin_bookings')

# Success page view after successful booking
class SuccessPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'backend/success_page.html')
    
def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterEmailForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'backend/subscribe.html')
    return redirect('/')

def toggle_paid_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Toggle the is_paid status
    booking.is_paid = not booking.is_paid
    booking.save()

    # Redirect back to the admin bookings page
    return redirect('admin_bookings')

def toggle_confirm_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        booking.confirmed = not booking.confirmed
        booking.save()
    return redirect('admin_bookings')