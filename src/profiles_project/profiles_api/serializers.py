from rest_framework import serializers
from django.contrib.auth import authenticate
from . import models


class HelloSerializer(serializers.Serializer):
    """Serializes a name field for testing our APIView."""

    name = serializers.CharField(max_length=10)


class UserProfileSerializer(serializers.ModelSerializer):
    """A serializer for our user profile objects."""

    password_confirm = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = models.UserProfile
        fields = (
            'id',
            'email',
            'name',
            'password',
            'password_confirm',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """Check that both passwords match."""

        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        """Create and return a new user."""

        validated_data.pop('password_confirm')

        user = models.UserProfile.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )

        return user


class ProfileFeedItemSerializer(serializers.ModelSerializer):
    """A serializer for profile feed items."""

    class Meta:
        model = models.ProfileFeedItem
        fields = ('id', 'user_profile', 'status_text', 'created_on')
        extra_kwargs = {
            'user_profile': {'read_only': True}
        }


class AuthTokenSerializer(serializers.Serializer):
    """Serializes the user authentication credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    'Unable to authenticate with the provided credentials.',
                    code='authorization',
                )
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
            )

        attrs['user'] = user
        return attrs

class PasswordChangeSerializer(serializers.Serializer):
    """Serializes password change requests."""

    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate the old password and new password confirmation."""

        user = self.context['request'].user

        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({
                'old_password': 'The old password is incorrect.'
            })

        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })

        return attrs
class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializes password reset requests."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializes password reset confirmation."""

    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
    )
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        """Check that both new passwords match."""

        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })

        return attrs

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a user profile."""

    class Meta:
        model = models.UserProfile
        fields = (
            'id',
            'email',
            'name',
            'email_verified',
        )
        read_only_fields = (
            'id',
            'email',
            'email_verified',
        )

class AccountStatusSerializer(serializers.Serializer):
    """Serializer for account activation and deactivation."""

    is_active = serializers.BooleanField()
