from rest_framework import permissions

class UpdateOwnProfile(permissions.BasePermission):
    """Controls profile access based on user role."""

    def has_object_permission(self, request, view, obj):
        """Check profile access based on user role."""

        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.is_staff:
            return True

        return obj.id == request.user.id

class PostOwnStatus(permissions.BasePermission):
    """Controls feed item access based on user role."""

    def has_object_permission(self, request, view, obj):
        """Check feed item access based on user role."""

        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.is_staff:
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

class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        """Check if the user is an admin."""

        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )

class IsStaff(permissions.BasePermission):
    """Allows access only to staff users."""

    def has_permission(self, request, view):
        """Check if the user is a staff member."""

        return (
            request.user.is_authenticated
            and request.user.is_staff
        )
