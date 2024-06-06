from rest_framework import serializers
from .models import Hotel, Review, FinanceReport

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
