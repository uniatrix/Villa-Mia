from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q
from django.utils import timezone
from django.views import View
from .forms import RoomForm, RoomCategoryForm, BookingForm, NewsletterEmailForm
from .models import Room, Booking, Category, NewsletterEmail, RoomImage
from datetime import timedelta
import datetime

def index(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.new_reservation = True  # Ensure this is set for new reservations
            booking.save()
            return redirect('success_page')
    else:
        form = BookingForm()
    return render(request, "backend/index.html", {'form': form})

def category_rooms(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    rooms = Room.objects.filter(category=category)

    # Filter rooms by availability for non-admin users
    if not request.user.is_staff:
        rooms = rooms.filter(available=True)
    
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if check_in and check_out:
        check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()

        # Filter out rooms that have bookings within the selected dates
        rooms = rooms.filter(
            ~Q(booking__check_in__lte=check_out_date, booking__check_out__gte=check_in_date)
        ).distinct()

    if request.method == 'POST':
        form = RoomCategoryForm(request.POST)
        if form.is_valid():
            room_id = request.POST.get('room_id')
            room = Room.objects.get(id=room_id)
            room.category = form.cleaned_data['category']
            room.available = 'available' in request.POST
            room.save()
            return redirect('category_rooms', category_id=category.id)
    else:
        form = RoomCategoryForm()
    
    return render(request, 'backend/category_rooms.html', {
        'category': category, 
        'rooms': rooms, 
        'form': form, 
        'check_in': check_in, 
        'check_out': check_out
    })

@user_passes_test(lambda u: u.is_staff)
def add_room_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            images = [request.FILES.get('image_1'), request.FILES.get('image_2'), request.FILES.get('image_3'), request.FILES.get('image_4')]
            for image in images:
                if image:
                    RoomImage.objects.create(room=room, image=image)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'rooms/add/'))
    else:
        form = RoomForm()
    return render(request, 'backend/add_room.html', {'form': form})

def load_rooms(request):
    category_id = request.GET.get('category_id')
    rooms = Room.objects.filter(category_id=category_id).order_by('title')
    return JsonResponse(list(rooms.values('id', 'title')), safe=False)

@user_passes_test(lambda u: u.is_staff)
def admin_bookings(request):
    # Archive bookings with past checkout date
    past_checkouts = Booking.objects.filter(check_out__lt=timezone.now(), archived=False)
    for booking in past_checkouts:
        booking.archived = True
        booking.room.check_in = None
        booking.room.check_out = None
        booking.save()

    bookings = Booking.objects.filter(archived=False)
    
    # Filtering logic
    nome = request.GET.get('nome')
    data = request.GET.get('data')
    apartamento = request.GET.get('apartamento')
    telefone = request.GET.get('telefone')

    if nome:
        bookings = bookings.filter(guest_name__icontains=nome)
    if data:
        bookings = bookings.filter(check_in__lte=data, check_out__gte=data)
    if apartamento:
        bookings = bookings.filter(room__id=apartamento)
    if telefone:
        bookings = bookings.filter(phone_number__icontains=telefone)
    
    rooms = Room.objects.all()

    return render(request, 'backend/admin_bookings.html', {
        'bookings': bookings,
        'rooms': rooms,
    })

def check_availability(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    bookings = Booking.objects.filter(room=room).exclude(check_out__lt=datetime.date.today())
    images = room.images.all()

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
        'form': form,
        'images': images
    })

@user_passes_test(lambda u: u.is_staff)
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('admin_bookings')

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
    booking.is_paid = not booking.is_paid
    booking.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'admin_bookings'))

def toggle_confirm_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        booking.confirmed = not booking.confirmed
        booking.new_reservation = not booking.confirmed  # Mark as not new when confirmed
        booking.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'admin_bookings'))

def new_reservations_count(request):
    if request.user.is_staff:
        count = Booking.objects.filter(new_reservation=True).count()
        return JsonResponse({'count': count})
    else:
        return JsonResponse({'count': 0})

@user_passes_test(lambda u: u.is_staff)
def archived_bookings(request):
    # Archive bookings with past checkout date
    past_checkouts = Booking.objects.filter(check_out__lt=timezone.now(), archived=False)
    for booking in past_checkouts:
        booking.archived = True
        booking.room.check_in = None
        booking.room.check_out = None
        booking.save()

    bookings = Booking.objects.filter(archived=True)
    
    # Filtering logic
    nome = request.GET.get('nome')
    data = request.GET.get('data')
    apartamento = request.GET.get('apartamento')
    telefone = request.GET.get('telefone')

    if nome:
        bookings = bookings.filter(guest_name__icontains=nome)
    if data:
        bookings = bookings.filter(check_in__lte=data, check_out__gte=data)
    if apartamento:
        bookings = bookings.filter(room__id=apartamento)
    if telefone:
        bookings = bookings.filter(phone_number__icontains=telefone)
    
    rooms = Room.objects.all()

    return render(request, 'backend/archived_bookings.html', {
        'bookings': bookings,
        'rooms': rooms,
    })

def archive_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        booking.archived = not booking.archived
        if booking.archived:
            booking.room.check_in = None
            booking.room.check_out = None
        booking.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'admin_bookings'))

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RoomForm
from .models import Room, RoomImage

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import RoomForm
from .models import Room, RoomImage

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_room_details(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            room = form.save(commit=False)
            room.save()

            # Handle additional images
            images = [
                request.FILES.get('image_1'),
                request.FILES.get('image_2'),
                request.FILES.get('image_3'),
                request.FILES.get('image_4')
            ]
            existing_images = RoomImage.objects.filter(room=room).order_by('id')

            for idx, new_image in enumerate(images, start=1):
                if new_image:
                    # Replace the existing image if it exists, otherwise create a new one
                    if len(existing_images) >= idx:
                        existing_image = existing_images[idx - 1]
                        existing_image.image = new_image
                        existing_image.save()
                    else:
                        RoomImage.objects.create(room=room, image=new_image)

            return redirect('check_availability', room_id=room.id)
        else:
            print("Form is not valid")
            print(form.errors)
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'backend/edit_room.html', {'form': form, 'room': room})
