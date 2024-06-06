# core/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Hotel, Review, FinanceReport
from .serializers import HotelSerializer, ReviewSerializer, FinanceReportSerializer
from .permissions import IsSystemAdmin, IsHotelAdmin

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSystemAdmin()]
        if self.action in ['approve', 'decline']:
            return [IsSystemAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        hotel = self.get_object()
        hotel.is_approved = True
        hotel.save()
        return Response({'status': 'hotel approved'})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        hotel = self.get_object()
        hotel.is_approved = False
        hotel.save()
        return Response({'status': 'hotel declined'})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsHotelAdmin])
    def respond(self, request, pk=None):
        review = self.get_object()
        if review.hotel.admin != request.user:
            return Response({'status': 'not authorized'}, status=403)
        response_text = request.data.get('response', '')
        review.response = response_text
        review.responded_at = timezone.now()
        review.save()
        return Response({'status': 'response added'})

class FinanceReportViewSet(viewsets.ModelViewSet):
    queryset = FinanceReport.objects.all()
    serializer_class = FinanceReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return FinanceReport.objects.all()
        return FinanceReport.objects.filter(hotel__admin=self.request.user)
