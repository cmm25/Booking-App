from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import UserManager
from rest_framework_simplejwt.tokens import RefreshToken

AUTH_PROVIDERS = {'email': 'email', 'google': 'google'}
ROLE_CHOICES = [
    ('client', 'Client'),
    ('hotel_admin', 'Hotel Admin'),
    ('system_admin', 'System Admin'),
]

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hotels')
    image = models.ImageField(upload_to='hotel_images/', null=True, blank=True)
    video = models.FileField(upload_to='hotel_videos/', null=True, blank=True)

    def __str__(self):
        return self.name

class RoomCategory(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_categories', default=0)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)
    video = models.FileField(upload_to='room_videos/', null=True, blank=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.number} - {self.category.name}"
class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('RESERVED', 'Reserved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='RESERVED')
    is_checked_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.room.hotel.name} - {self.room.category.name}"

    def save(self, *args, **kwargs):
        # Ensure room availability is updated when booking status changes
        if self.payment_status == 'RESERVED':
            self.room.is_available = False
        elif self.payment_status == 'CANCELLED':
            self.room.is_available = True
        self.room.save()
        super().save(*args, **kwargs)


class Review(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
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

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name=_('email address'), unique=True)
    first_name = models.CharField(verbose_name=_('first name'), max_length=30, blank=True)
    last_name = models.CharField(verbose_name=_('last name'), max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    objects = UserManager()

    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

class OneTimePassword(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.user.first_name} - passcode"
