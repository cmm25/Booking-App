from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    is_approved = models.BooleanField(default=False)
    admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hotel')

    def __str__(self):
        return self.name

class RoomCategory(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    number = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.hotel.name} - {self.number} - {self.category.name}"

class Booking(models.Model):
    payment_status =[
        ('RESERVED', 'Reserved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    payment_status = models.CharField(max_length=10, choices=payment_status, default='reserved')
    is_checked_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.room.hotel.name} - {self.room.category.name}"

class Review(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Review by {self.client} on {self.hotel.name}'

class FinanceReport(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='finance_reports')
    rooms_paid = models.IntegerField()
    money_earned = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Finance report for {self.hotel.name}'
