from rest_framework import permissions


class UpdateOwnProfile(permissions.BasePermission):
    """Allows user to edit their own profile."""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own profile."""

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id

class PostOwnStatus(permissions.BasePermission):
    """Allows user to update their own status."""

    def has_object_permission(self, request, view, obj):
        """Check if the user is trying to update their own status."""

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user_profile.id == request.user.id

class IsStaffOrOwnDeactivation(permissions.BasePermission):
    """Allows staff users to manage accounts or users to deactivate themselves."""

    def has_object_permission(self, request, view, obj):
        """Check account status management permissions."""

        if not request.user.is_authenticated:
            return False

        # Staff users can activate or deactivate any account.
        if request.user.is_staff:
            return True

        # Regular users can only deactivate their own account.
        return (
            obj.id == request.user.id
            and request.data.get('is_active') is False
        )
