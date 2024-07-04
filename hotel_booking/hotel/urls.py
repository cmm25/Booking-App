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
    path('', include(router.urls)),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('verify-email/', views.VerifyUserEmail.as_view(), name='verify'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('password-reset/', views.PasswordResetRequest.as_view(), name='password-reset'),
    path('profile/', views.TestAuthenticationView.as_view(), name='profile'),
    path('password-reset-confirmed/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', views.SetNewPassword.as_view(), name='set-new-password'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('google/', views.GoogleSignInView.as_view(), name='google'),
    path('pending-hotels/', views.PendingHotelListView.as_view(), name='pending-hotels'),
    path('approve-hotel/<int:pk>/',views.ApproveHotelView.as_view(), name='approve-hotel'),
    path('decline-hotel/<int:pk>/', views.DeclineHotelView.as_view(), name='decline-hotel'),
]
