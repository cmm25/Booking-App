from rest_framework import viewsets
from rest_framework import status
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
            user_instance = serializer.save()
            user = serializer.data
            sendOtpEmail(user['email'])
            print(user)
            return Response({
                'data': user,
                'message': f"Hello {user_instance.first_name}, thank you for signing up. The passcode is {user_instance.passcode}"  # assuming 'passcode' is an attribute of user_instance
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otpcode= request.data.get('otp')
        try:
            user_code=OneTimePassword.objects.get(code = otpcode)
            user= user_code.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({'status': 'Email verified successfully'}, status= status.HTTP_200_OK)
            else:
                return Response({'status': 'Email already verified'}, status= status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({'status': 'Passcode not provided'}, status= status.HTTP_404_NOT_FOUND)
        


class LoginUserView(GenericAPIView):
    serializer_class= LoginSerializer

    def post(self,request):
        serializer=self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status= status.HTTP_200_OK)

class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'status': 'authenticated'}, status=status.HTTP_200_OK)

class PasswordResetRequest(GenericAPIView):
    serializer_class = PasswordResetSerializer
    def post(self, request):
        serializer = self.serializer_class(data = request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response ({'message':' A link has been sent to reset your password'}, status= status.HTTP_200_OK)


class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id = user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error':'Token is not valid, please request a new one'}, status= status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'Token is valid','uidb64':uidb64, 'token':token}, status= status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({'error':'Token is not valid, please request a new one'}, status= status.HTTP_401_UNAUTHORIZED)
        

class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self,request):
        serializer =self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        return Response ({'message': "Password has been reset successfully"}, status = status.HTTP_200_OK)
