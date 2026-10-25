from rest_framework.permissions import BasePermission

from accounts.models import User


class IsAgent(BasePermission):
    """Allows access only to support agents and staff users."""

    message = "Only support agents can do this."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (user.is_staff or user.role == User.Role.AGENT)
        )
