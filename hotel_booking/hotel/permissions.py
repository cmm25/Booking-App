# users/permissions.py
from rest_framework.permissions import BasePermission

class IsSystemAdmin(BasePermission):
    """
    Permission class for system administrators.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_system_admin

class IsHotelAdmin(BasePermission):
    """
    Permission class for hotel managers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_hotel_manager

class IsClient(BasePermission):
    """
    Permission class for clients (regular users).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client


#remember to define the model to choose between above