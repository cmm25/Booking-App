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

class Review(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Review by {self.client} on {self.hotel}'

class FinanceReport(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='finance_reports')
    rooms_paid = models.IntegerField()
    money_earned = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Finance report for {self.hotel}'
