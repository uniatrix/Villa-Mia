from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)  # Main image
    capacity = models.IntegerField()
    ac = models.BooleanField(default=False)
    tv = models.BooleanField(default=True)
    wifi = models.BooleanField(default=True)
    bathtub = models.BooleanField(default=False)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='room_images/')

    def __str__(self):
        return f"Image for {self.room.title}"

class Booking(models.Model):
    phone_regex = RegexValidator(regex=r'^\d{1,13}$', message="Phone number must be numeric and up to 13 digits")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=13, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    new_reservation = models.BooleanField(default=True, help_text="Indicates if the reservation is new")
    is_paid = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.guest_name or (self.user.username if self.user else 'Unknown')} - {self.room.title} from {self.check_in} to {self.check_out}"
    
class NewsletterEmail(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
