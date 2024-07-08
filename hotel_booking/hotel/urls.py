from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'hotels', views.HotelViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'room-categories', views.RoomCategoryViewSet)
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
    path('pending-hotels/', views.PendingHotelsView.as_view(), name='pending-hotels'),
    path('approve-hotel/<int:pk>/', views.HotelViewSet.as_view({'post': 'approve'}), name='approve-hotel'),
    path('decline-hotel/<int:pk>/', views.HotelViewSet.as_view({'post': 'decline'}), name='decline-hotel'),
    path('approved-hotels/', views.ApprovedHotelsView.as_view(), name='approved-hotels'),
    path('approved-hotels/<int:pk>/', views.ApprovedHotelDetailView.as_view(), name='approved-hotel-detail'),
]
