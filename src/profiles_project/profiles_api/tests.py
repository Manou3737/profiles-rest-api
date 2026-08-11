from django.test import TestCase

# Create your tests here.
from django.test import TestCase

from . import models


class UserProfileModelTests(TestCase):
    """Tests for the UserProfile model."""

    def test_create_user_profile(self):
        """Test creating a new user profile."""

        user = models.UserProfile.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123',
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
