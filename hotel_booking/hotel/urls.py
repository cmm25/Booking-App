from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, ReviewViewSet, FinanceReportViewSet

router = DefaultRouter()
router.register(r'hotels', HotelViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'finance-reports', FinanceReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
