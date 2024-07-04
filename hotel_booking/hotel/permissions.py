# users/permissions.py
from rest_framework.permissions import BasePermission

class IsSystemAdmin(BasePermission):
    """
    Permission class for system administrators.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'system_admin'
class IsHotelAdmin(BasePermission):
    """
    Permission class for hotel managers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'hotel_admin'

    def has_object_permission(self, request, view, obj):
        # Ensure hotel admin can only manage rooms if associated hotel is approved
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return obj.admin == request.user and obj.admin.hotel.is_approved
        return True

class IsClient(BasePermission):
    """
    Permission class for clients (regular users).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client


#remember to define the model to choose between above