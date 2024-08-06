from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('category/<int:category_id>/', views.category_rooms, name='category_rooms'),
    path('rooms/add/', views.add_room_view, name='add_room_view'),
    path('ajax/load-rooms/', views.load_rooms, name='ajax_load_rooms'),
    path('admin-bookings/', views.admin_bookings, name='admin_bookings'),
    path('archived-bookings/', views.archived_bookings, name='archived_bookings'),
    path('check_availability/<int:room_id>/', views.check_availability, name='check_availability'),
    path('success_page/', views.SuccessPageView.as_view(), name='success_page'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('toggle-paid-status/<int:booking_id>/', views.toggle_paid_status, name='toggle_paid_status'),
    path('toggle-confirm-status/<int:booking_id>/', views.toggle_confirm_status, name='toggle_confirm_status'),
    path('new_reservations_count/', views.new_reservations_count, name='new_reservations_count'),
    path('archive-booking/<int:booking_id>/', views.archive_booking, name='archive_booking'),
    path('edit-room/<int:room_id>/', views.edit_room_details, name='edit_room_details'),  # New URL pattern
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
