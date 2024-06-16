from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from .models import Hotel, Review, FinanceReport, Room, Booking
from .serializers import HotelSerializer,UserRegistrationSerializer, ReviewSerializer, FinanceReportSerializer, RoomSerializer, BookingSerializer
from .permissions import IsSystemAdmin, IsHotelAdmin
from .utils import sendOtpEmail

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

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        booking = self.get_object()
        payment_amount = request.data.get('payment_amount')
        if payment_amount and float(payment_amount) >= booking.room.category.price:
            booking.payment_status = 'paid'
            booking.save()
            return Response({'status': 'payment successful'})
        else:
            return Response({'status': 'insufficient payment amount'}, status=400)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.payment_status == 'reserved' and booking.user == request.user:
            booking.payment_status = 'cancelled'
            booking.save()
            return Response({'status': 'reservation cancelled'})
        else:
            return Response({'status': 'cancellation not allowed'}, status=400)

class RegisterUserView(GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            sendOtpEmail(user['email'])
            print(user)
            return Response({'data': user,
                             'message': f'Hello {user.first_name} thank you for signing up
                              the passcode is '}, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)