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
]
