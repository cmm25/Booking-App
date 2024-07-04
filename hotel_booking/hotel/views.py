from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from .models import Hotel, Review, FinanceReport, Room, Booking, User
from .serializers import PasswordResetSerializer, SetNewPasswordSerializer, HotelSerializer, UserRegistrationSerializer, ReviewSerializer, FinanceReportSerializer, RoomSerializer, BookingSerializer, LoginSerializer
from .permissions import IsSystemAdmin, IsHotelAdmin
from .utils import sendOtpEmail
from .models import OneTimePassword
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import Hotel, Review, FinanceReport, Room, Booking, User, OneTimePassword
from .serializers import (
    GoogleSignInSerializer, PasswordResetSerializer, LogoutUserSerializer,
    SetNewPasswordSerializer, HotelSerializer, UserRegistrationSerializer,
    ReviewSerializer, FinanceReportSerializer, RoomSerializer, BookingSerializer,
    LoginSerializer
)
from .permissions import IsSystemAdmin, IsHotelAdmin
from .utils import sendOtpEmail

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated, IsHotelAdmin]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsHotelAdmin()]
        elif self.action in ['approve', 'decline', 'pending']:
            return [IsSystemAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsSystemAdmin])
    def approve(self, request, pk=None):
        hotel = self.get_object()
        hotel.is_approved = True
        hotel.save()
        return Response({'status': 'hotel approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsSystemAdmin])
    def decline(self, request, pk=None):
        hotel = self.get_object()
        hotel.is_approved = False
        hotel.save()
        return Response({'status': 'hotel declined'})

    @action(detail=False, methods=['get'], permission_classes=[IsSystemAdmin])
    def pending(self, request):
        pending_hotels = Hotel.objects.filter(is_approved=False)
        serializer = self.get_serializer(pending_hotels, many=True)
        return Response(serializer.data)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_hotel_admin:
            return Review.objects.filter(hotel__admin=self.request.user)
        elif self.request.user.is_client:
            return Review.objects.filter(user=self.request.user)
        else:
            return Review.objects.none()

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        review = self.get_object()
        if request.user.is_hotel_admin and review.hotel.admin != request.user:
            return Response({'status': 'not authorized'}, status=status.HTTP_403_FORBIDDEN)
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
        if self.request.user.is_hotel_admin:
            hotel = self.request.user.hotel
            return FinanceReport.objects.filter(hotel=hotel)
        else:
            return FinanceReport.objects.none()

    @action(detail=False, methods=['get'])
    def filter_by_year_month(self, request):
        if not self.request.user.is_hotel_admin:
            return Response({'detail': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        hotel = self.request.user.hotel
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        queryset = FinanceReport.objects.filter(hotel=hotel)

        if year:
            queryset = queryset.filter(created_at__year=year)
        if month:
            queryset = queryset.filter(created_at__month=month)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, IsHotelAdmin]

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
            return Response({'status': 'payment successful'}, status=status.HTTP_200_OK)
        return Response({'status': 'insufficient payment amount'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.payment_status == 'reserved' and booking.user == request.user:
            booking.payment_status = 'cancelled'
            booking.save()
            return Response({'status': 'reservation cancelled'}, status=status.HTTP_200_OK)
        return Response({'status': 'cancellation not allowed'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterUserView(GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_instance = serializer.save()
            sendOtpEmail(user_instance.email)
            return Response({
                'data': serializer.data,
                'message': f"Hello {user_instance.first_name}, thank you for signing up. The passcode is {user_instance.password}"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            user_code = OneTimePassword.objects.get(code=otp_code)
            user = user_code.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({'status': 'Email verified successfully'}, status=status.HTTP_200_OK)
            return Response({'status': 'Email already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({'status': 'Passcode not provided'}, status=status.HTTP_404_NOT_FOUND)

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Extract relevant data from serializer.validated_data
        response_data = {
            "email": serializer.validated_data['email'],
            "full_name": serializer.validated_data['full_name'],
            "role": serializer.validated_data['role'],
            "access_token": serializer.validated_data['access_token'],
            "refresh_token": serializer.validated_data['refresh_token'],
        }

        return Response(response_data, status=status.HTTP_200_OK)

class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'status': 'authenticated'}, status=status.HTTP_200_OK)

class PasswordResetRequest(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'A link has been sent to reset your password'}, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Token is valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

class GoogleSignInView(GenericAPIView):
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data['access_token']
        return Response(data, status=status.HTTP_200_OK)
    

class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PendingHotelListView(generics.ListAPIView):
    queryset = Hotel.objects.filter(is_approved=False)
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]

class ApproveHotelView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    def post(self, request, pk):
        try:
            hotel = Hotel.objects.get(pk=pk)
            hotel.is_approved = True
            hotel.save()
            return Response({'status': 'Hotel approved'}, status=status.HTTP_200_OK)
        except Hotel.DoesNotExist:
            return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

class DeclineHotelView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    def post(self, request, pk):
        try:
            hotel = Hotel.objects.get(pk=pk)
            hotel.delete()
            return Response({'status': 'Hotel declined'}, status=status.HTTP_200_OK)
        except Hotel.DoesNotExist:
            return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)