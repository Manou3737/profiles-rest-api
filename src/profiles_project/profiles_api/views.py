from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import filters
from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from . import serializers
from . import models
from . import permissions

# Create your views here.

class HelloApiView(APIView):
    """Test the api view ."""

    serializer_class = serializers.HelloSerializer

    def get(self, request, format=None):
        """Returns a list of APIView features."""

        an_apiview = [
        'Uses HTTP methods as function(get, post, patch, put, delete)',
        'It is similar to a traditional Django view',
        'Gives you the most control over your logic',
        'Is mapped manually to urls'

        ]
        return Response({
        'message': 'Hello',
        'an_apiview': an_apiview
        })

    def post(self, request):
        """Create a hello message with our name."""

        serializer = serializers.HelloSerializer(data=request.data)

        if serializer.is_valid():
            name = serializer.data.get('name')
            message = 'Hello {0}'.format(name)
            return Response({
            'message': message
            })

        else:
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """Handles updating an object."""
        return Response({'method':'put'})

    def patch(self, request, pk=None):
        """Handles a partially updated object with the fields provided."""
        return Response({'method':'patch'})

    def delete(self, request, pk=None):
        """Deletes an object."""
        return Response({'method': 'delete'})

class HelloViewSet(viewsets.ViewSet):
    """Tests API ViewSet."""

    serializer_class = serializers.HelloSerializer

    def list(self, request):
        """Return a hello message."""

        a_viewset = [
        'Uses actions(list, create, retrieve, update, partial_update)',
        'Automatically maps to URLs using Routers',
        'Provides more functionality with less code.'
        ]

        return Response({
        'message': 'Hello',
        'a_viewset': a_viewset
        })

    def create(self, request):
        """Creates a new hello message."""

        serializer = serializers.HelloSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.data.get('name')
            message = 'Hello {0}'.format(name)
            return Response({'message': message})

        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handles getting an object by its ID."""
        return Response({'http_method': 'Get'})

    def update(self, request,pk=None):
        """Handles updating an object."""
        return Response({'http_method': 'PUT'})

    def partial_update(self, request,pk=None):
        """Handles updating part of an object."""
        return Response({'http_method': 'PATCH'})

    def destroy(self, request, pk=None):
        """Handles removing an object."""
        return Response({'http_method': 'DELETE'})

class UserProfileViewset(viewsets.ModelViewSet):
    """Handles creating and updating profiles."""

    def get_serializer_class(self):
        """Return appropriate serializer based on the action."""

        if self.action == 'create':
            return serializers.UserProfileSerializer

        return serializers.UserProfileUpdateSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path='admin-users',
        permission_classes=(permissions.IsAdmin,),
    )
    def admin_users(self, request):
        """Return all users for administrators."""

        queryset = self.get_queryset()
        serializer = serializers.UserProfileUpdateSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    queryset = models.UserProfile.objects.all()
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)

class RegisterViewSet(viewsets.ViewSet):
    """Handles user registration."""

    serializer_class = serializers.UserProfileSerializer

    def create(self, request):
        """Create a new user account and send verification email."""

        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verification_url = (
            f'http://127.0.0.1:8000/api/verify-email/'
            f'?uid={uid}&token={token}'
        )

        from django.core.mail import send_mail

        send_mail(
            'Verify your email address',
            (
                f'Hello {user.name},\n\n'
                f'Please verify your email address by visiting this link:\n\n'
                f'{verification_url}\n\n'
                f'Thank you.'
            ),
            'noreply@example.com',
            [user.email],
        )

        return Response(
            {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'email_verified': user.email_verified,
            },
            status=status.HTTP_201_CREATED,
        )

class EmailVerificationViewSet(viewsets.ViewSet):
    """Handles email verification."""

    def list(self, request):
        """Verify a user's email address."""

        uid = request.query_params.get('uid')
        token = request.query_params.get('token')

        if not uid or not token:
            return Response(
                {'detail': 'UID and token are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = models.UserProfile.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError,
                models.UserProfile.DoesNotExist):
            return Response(
                {'detail': 'Invalid email verification link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.email_verified:
            return Response(
                {'detail': 'Email address is already verified.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Invalid or expired email verification token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True
        user.save(update_fields=['email_verified'])

        return Response(
            {'detail': 'Email address verified successfully.'},
            status=status.HTTP_200_OK,
        )


class LoginViewSet(viewsets.ViewSet):
    """Checks email and password and returns JWT tokens."""

    serializer_class = serializers.AuthTokenSerializer

    def create(self, request):
        """Validate credentials and return JWT token."""

        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutViewSet(viewsets.ViewSet):
    """Handles user logout by blacklisting the refresh token."""

    def create(self, request):
        """Blacklist the refresh token."""

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except TokenError:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_205_RESET_CONTENT,
        )

class PasswordChangeViewSet(viewsets.ViewSet):
    """Handles changing the authenticated user's password."""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.PasswordChangeSerializer

    def create(self, request):
        """Change the authenticated user's password."""

        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK,
        )

class PasswordResetRequestViewSet(viewsets.ViewSet):
    """Handles password reset requests."""

    serializer_class = serializers.PasswordResetRequestSerializer

    def create(self, request):
        """Generate a password reset token for the user."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = models.UserProfile.objects.get(email=email)
        except models.UserProfile.DoesNotExist:
            return Response(
                {'detail': 'No user found with this email address.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = default_token_generator.make_token(user)

        return Response(
            {
                'detail': 'Password reset token generated successfully.',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmViewSet(viewsets.ViewSet):
    """Handles password reset confirmation."""

    serializer_class = serializers.PasswordResetConfirmSerializer

    def create(self, request):
        """Set a new password using the reset token."""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = models.UserProfile.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError,
                models.UserProfile.DoesNotExist):
            return Response(
                {'detail': 'Invalid password reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Invalid or expired password reset token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {'detail': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK,
        )

class AccountStatusViewSet(viewsets.ViewSet):
    """Handles account activation and deactivation."""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsStaffOrOwnDeactivation,)
    serializer_class = serializers.AccountStatusSerializer

    def partial_update(self, request, pk=None):
        """Activate or deactivate a user account."""

        try:
            user = models.UserProfile.objects.get(pk=pk)
        except models.UserProfile.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.check_object_permissions(request, user)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.is_active = serializer.validated_data['is_active']
        user.save(update_fields=['is_active'])

        return Response(
            {
                'id': user.id,
                'email': user.email,
                'is_active': user.is_active,
            },
            status=status.HTTP_200_OK,
        )

class UserProfileFeedViewset(viewsets.ModelViewSet):
    """Handles creating, reading and updating profile feed items."""

    authentication_classes = (JWTAuthentication,)
    serializer_class = serializers.ProfileFeedItemSerializer
    queryset = models.ProfileFeedItem.objects.all()
    permission_classes = (permissions.PostOwnStatus, IsAuthenticated)

    def perform_create(self, serializer):
        """Sets the user profile to the logged in user."""

        serializer.save(user_profile=self.request.user)
