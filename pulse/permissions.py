from rest_framework.permissions import BasePermission
from .models import UserProfile

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            return UserProfile.objects.get(user=request.user).role == UserProfile.Role.ADMIN
        except UserProfile.DoesNotExist:
            return False