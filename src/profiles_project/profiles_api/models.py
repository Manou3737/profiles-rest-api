from django.db import models

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

# Create your models here.
class UserProfileManager(BaseUserManager):
    """Helps django work with our custom model."""

    def create_user(self, email, name, password=None):
        """create a new user profile object."""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """Creates and save a new superuser with a given details."""

        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Represents a user profile inside our system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    email_verified = models.BooleanField(default=False)
    is_active= models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        """Use to get a user full name."""

        return self.name

    def get_short_name(self):
        """Use to get a user short name."""
        return self.name

    def __str__(self):
        """Django uses this when it needs to convert the object to a string."""
        return self.email

class ProfileFeedItem(models.Model):
    """Profile status update."""

    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    status_text = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add =True)

    def __str__(self):
        """Return the models as a string."""
        return self.status_text

class AuditLog(models.Model):
    """Records important actions performed in the system."""

    ACTION_CHOICES = (
        ('LOGIN', 'Login'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('ACCOUNT_ACTIVATED', 'Account Activated'),
        ('ACCOUNT_DEACTIVATED', 'Account Deactivated'),
        ('ACCOUNT_CHANGE', 'Account Change'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
    )

    user = models.ForeignKey(
        'UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f'{self.action} - {self.user}'

class SecurityEvent(models.Model):
    """Records security-related events."""

    EVENT_TYPES = (
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('PASSWORD_CHANGED', 'Password Changed'),
        ('ACCOUNT_ACTIVATED', 'Account Activated'),
        ('ACCOUNT_DEACTIVATED', 'Account Deactivated'),
        ('ACCOUNT_CHANGE', 'Account Change'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access'),
    )

    user = models.ForeignKey(
        'UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f'{self.event_type} - {self.user}'
