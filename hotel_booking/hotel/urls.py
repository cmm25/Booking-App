from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'hotels', views.HotelViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'finance_reports', views.FinanceReportViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'bookings', views.BookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterUserView.as_view(), name='register'), 
    path('api/verify-email/',views.VerifyUserEmail.as_view(), name= 'verify'),
    path('api/login/', views.LoginUserView.as_view(), name='Login'),
    path('api/password-reset/', views.PasswordResetRequest.as_view(), name='password-reset'),
    path('api/profile/',views.TestAuthenticationView.as_view, name= 'granted'),
    path('api/password-reset-confirmed/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('api/set-new-password/', views.SetNewPassword.as_view(), name='set-new-password')
]
