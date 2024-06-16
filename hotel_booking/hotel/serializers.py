from rest_framework import serializers
from .models import User, Hotel, Review, FinanceReport, Room, Booking, RoomCategory

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

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

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only= True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only= True)

    class Meta:
        model= User
        fields = ['email','first_name','last_name','password','password2']
    
    def validate(self, attrs):
        password = attrs.get('password','')
        password2 = attrs.get('password2','')
        if password != password2:
            raise serializers.ValidationError('Passwords should match')
        return attrs
    
    def create(self, validated_data):
        user= User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get['first_name'],
            last_name=validated_data.get['last_name'],
            password=validated_data.get['password']
        )

        return user