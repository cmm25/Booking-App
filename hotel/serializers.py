from rest_framework import serializers
from .models import User, Hotel, Review, FinanceReport, Room, Booking, RoomCategory, ROLE_CHOICES, OneTimePassword
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from .utils import send_email, Google, register_social_user
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'address','id']
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class FinanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceReport
        fields = '__all__'

class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user'] 

    def validate(self, data):
        room = data['room']
        if not room.is_available:
            raise serializers.ValidationError("This room is not available.")
        return data

    def create(self, validated_data):
        room = validated_data['room']
        booking = Booking.objects.create(**validated_data)
        room.is_available = False
        room.save()
        return booking

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, default='client')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2', 'role']
    
    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError('Passwords should match')
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            role=validated_data.get('role')
        )
        return user
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    role = serializers.CharField(max_length=20, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'role', 'access_token', 'refresh_token', 'message']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')

        user = authenticate(request=request, email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_verified:
            raise AuthenticationFailed('Account is not verified')

        # Assuming tokens() returns a dictionary with access and refresh tokens
        user_tokens = user.tokens()

        return {
            'email': user.email,
            'full_name': user.get_full_name,  # Correctly calling get_full_name()
            'role': user.role,  # Accessing role directly from the user instance
            'access_token': str(user_tokens.get('access')),  # Convert to string if necessary
            'refresh_token': str(user_tokens.get('refresh')),  # Convert to string if necessary
        }
class PasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        request = self.context.get('request')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absolute_link = f"http://{site_domain}{relative_link}"
            email_message = f"Hi, use this link to reset your password: \n{absolute_link}"
            data = {
                'email_body': email_message,
                'to_email': user.email,
                'email_subject': 'Reset your password'
            }
            send_email(data)
        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only = True)
    token = serializers.CharField(write_only = True)
    class Meta:
        fields = ["password","confirm_password","uidb64","token"]

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            password = attrs.get('password')
            uidb64 = attrs.get('uidb64')
            confirm_password = attrs.get('confirm_password')
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user= User.objects.get(id=user_id)
            
            if PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed("Password reset link has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("Passwords do not match", 401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:  
            raise AuthenticationFailed('The reset link is invalid', 401)
        

class LogoutUserSerializer(serializers.ModelSerializer):
    refresh_token = serializers.CharField()
    default_error_message ={
        'bad_token': ('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')
        return attrs
    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')
        

class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length = 6)

    def validate_access_token(self,access_token):
        google_user_data = Google.validate_google_token(access_token)
        try:
            user_id = google_user_data['sub']

        except:
            raise serializers.ValidationError("Invalid Token")
        
        if google_user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise serializers.ValidationError(detail= 'Invalid client ID')
        email = google_user_data['email']
        first_name = google_user_data['given_name']
        last_name = google_user_data['family_name']
        provider = 'google'
        
        return register_social_user(provider, email, first_name, last_name)

class VerifyUserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneTimePassword
        fields = ['code', 'user']  

    def create(self, validated_data):
        return OneTimePassword.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.code = validated_data.get('code', instance.code)
        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance

class DeleteAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['password']

    def validate(self, attrs):
        password = attrs.get('password', '')
        user = self.context['request'].user
        
        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password, please try again')
        
        return attrs
