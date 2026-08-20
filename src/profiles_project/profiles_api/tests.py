from django.test import TestCase
from rest_framework.test import APIClient

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


class PublicUserApiTests(TestCase):
    """Test the publicly available user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user through the API."""

        payload = {
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'testpass123',
        }

        response = self.client.post('/api/profile/', payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], payload['email'])
        self.assertEqual(response.data['name'], payload['name'])

        user = models.UserProfile.objects.get(
            email=payload['email']
        )

        self.assertTrue(
            user.check_password(payload['password'])
        )

    def test_login_user(self):
        """Test that a user can log in and receive a token."""

        models.UserProfile.objects.create_user(
            email='login@example.com',
            name='Login User',
            password='testpass123',
        )

        payload = {
            'email': 'login@example.com',
            'password': 'testpass123',
        }

        response = self.client.post('/api/login/', payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test that invalid credentials are rejected."""

        models.UserProfile.objects.create_user(
            email='login@example.com',
            name='Login User',
            password='testpass123',
        )

        payload = {
            'email': 'login@example.com',
            'password': 'wrongpassword',
        }

        response = self.client.post('/api/login/', payload)

        self.assertEqual(response.status_code, 400)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.client = APIClient()

        self.user1 = models.UserProfile.objects.create_user(
            email='user1@example.com',
            name='User One',
            password='testpass123',
        )

        self.user2 = models.UserProfile.objects.create_user(
            email='user2@example.com',
            name='User Two',
            password='testpass123',
        )

    def test_user_cannot_update_other_user_profile(self):
        """Test that users cannot update another user's profile."""

        self.client.force_authenticate(user=self.user2)

        payload = {
            'email': 'hacked@example.com',
            'name': 'Hacked User',
            'password': 'newpassword123',
        }

        response = self.client.put(
            f'/api/profile/{self.user1.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 403)

    def test_user_cannot_update_other_user_feed(self):
        """Test that users cannot update another user's feed item."""

        feed_item = models.ProfileFeedItem.objects.create(
            user_profile=self.user1,
            status_text='User One post',
        )

        self.client.force_authenticate(user=self.user2)

        payload = {
            'status_text': 'Hacked post',
        }

        response = self.client.put(
            f'/api/feed/{feed_item.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 403)

    def test_user_can_create_feed_item(self):
        """Test that an authenticated user can create a feed item."""

        self.client.force_authenticate(user=self.user1)

        payload = {
            'status_text': 'My new post',
        }

        response = self.client.post(
            '/api/feed/',
            payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['status_text'],
            payload['status_text'],
        )
        self.assertEqual(
            response.data['user_profile'],
            self.user1.id,
        )

    def test_unauthenticated_user_cannot_create_feed_item(self):
        """Test that an unauthenticated user cannot create a feed item."""

        payload = {
            'status_text': 'Anonymous post',
        }

        response = self.client.post(
            '/api/feed/',
            payload,
        )

        self.assertEqual(response.status_code, 401)
