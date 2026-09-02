from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.test import TestCase
from django.core import mail

from . import models
from . import permissions

class HelloViewSetTests(TestCase):
    """Tests for HelloViewSet."""

    def setUp(self):
        self.client = APIClient()

    def test_list_hello_viewset(self):
        """Test GET list action."""

        response = self.client.get('/api/hello-viewset/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Hello')
        self.assertIn('a_viewset', response.data)

    def test_create_hello_viewset_success(self):
        """Test POST create action with valid data."""

        response = self.client.post(
            '/api/hello-viewset/',
            {'name': 'Manoucheka'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['message'],
            'Hello Manoucheka',
        )

    def test_create_hello_viewset_invalid_data(self):
        """Test POST create action with invalid data."""

        response = self.client.post(
            '/api/hello-viewset/',
            {'name': ''},
        )

        self.assertEqual(response.status_code, 400)

    def test_retrieve_hello_viewset(self):
        """Test GET retrieve action."""

        response = self.client.get('/api/hello-viewset/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['http_method'], 'Get')

    def test_update_hello_viewset(self):
        """Test PUT update action."""

        response = self.client.put(
            '/api/hello-viewset/1/',
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['http_method'], 'PUT')

    def test_partial_update_hello_viewset(self):
        """Test PATCH partial update action."""

        response = self.client.patch(
            '/api/hello-viewset/1/',
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['http_method'], 'PATCH')

    def test_destroy_hello_viewset(self):
        """Test DELETE destroy action."""

        response = self.client.delete('/api/hello-viewset/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['http_method'], 'DELETE')

class HelloApiViewTests(TestCase):
    """Tests for HelloApiView."""

    def setUp(self):
        self.client = APIClient()

    def test_get_hello_api_view(self):
        """Test GET request to HelloApiView."""

        response = self.client.get('/api/hello-view/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Hello')
        self.assertIn('an_apiview', response.data)

    def test_post_hello_api_view_success(self):
        """Test POST request with a valid name."""

        response = self.client.post(
            '/api/hello-view/',
            {'name': 'Manoucheka'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['message'],
            'Hello Manoucheka',
        )

    def test_post_hello_api_view_invalid_data(self):
        """Test POST request with invalid data."""

        response = self.client.post(
            '/api/hello-view/',
            {'name': ''},
        )

        self.assertEqual(response.status_code, 400)

    def test_put_hello_api_view(self):
        """Test PUT request to HelloApiView."""

        response = self.client.put(
            '/api/hello-view/',
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], 'put')

    def test_patch_hello_api_view(self):
        """Test PATCH request to HelloApiView."""

        response = self.client.patch(
            '/api/hello-view/',
            {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], 'patch')

    def test_delete_hello_api_view(self):
        """Test DELETE request to HelloApiView."""

        response = self.client.delete('/api/hello-view/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['method'], 'delete')

class RegisterViewSetTests(TestCase):
    """Tests for user registration."""

    def setUp(self):
        self.client = APIClient()

    def test_register_user_success(self):
        """Test successful user registration."""

        payload = {
            'email': 'register@example.com',
            'name': 'Registered User',
            'password': 'RegisterPassword123!',
            'password_confirm': 'RegisterPassword123!',
        }

        response = self.client.post(
            '/api/register/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data['email'],
            payload['email'],
        )

        self.assertEqual(
            response.data['name'],
            payload['name'],
        )

        self.assertFalse(
            response.data['email_verified']
        )

        user = models.UserProfile.objects.get(
            email=payload['email']
        )

        self.assertTrue(
            user.check_password(payload['password'])
        )

    def test_register_user_sends_verification_email(self):
        """Test that registration sends a verification email."""

        payload = {
            'email': 'verification@example.com',
            'name': 'Verification User',
            'password': 'RegisterPassword123!',
            'password_confirm': 'RegisterPassword123!',
        }

        response = self.client.post(
            '/api/register/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.to,
            [payload['email']],
        )

        self.assertEqual(
            email.subject,
            'Verify your email address',
        )

        self.assertIn(
            'Please verify your email address',
            email.body,
        )

    def test_register_user_rejects_invalid_data(self):
        """Test that invalid registration data is rejected."""

        payload = {
            'email': 'invalid-email',
            'name': '',
            'password': '123',
            'password_confirm': '456',
        }

        response = self.client.post(
            '/api/register/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)

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
            'password_confirm': 'testpass123',
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

class EmailVerificationTests(TestCase):
    """Tests for email verification."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='verify@example.com',
            name='Verification User',
            password='VerifyPassword123!',
        )

    def get_verification_data(self):
        """Generate a valid UID and verification token."""

        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )
        token = default_token_generator.make_token(self.user)

        return uid, token

    def test_email_verification_requires_uid_and_token(self):
        """Test that UID and token are required."""

        response = self.client.get(
            '/api/verify-email/',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'UID and token are required.',
        )

    def test_email_verification_rejects_invalid_uid(self):
        """Test that an invalid UID is rejected."""

        uid = urlsafe_base64_encode(force_bytes(999999))

        response = self.client.get(
            f'/api/verify-email/?uid={uid}&token=invalid-token',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid email verification link.',
        )

    def test_email_verification_rejects_invalid_token(self):
        """Test that an invalid verification token is rejected."""

        uid, _ = self.get_verification_data()

        response = self.client.get(
            f'/api/verify-email/?uid={uid}&token=invalid-token',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid or expired email verification token.',
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.email_verified)

    def test_email_verification_success(self):
        """Test that a valid token verifies the user's email."""

        uid, token = self.get_verification_data()

        response = self.client.get(
            f'/api/verify-email/?uid={uid}&token={token}',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['detail'],
            'Email address verified successfully.',
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.email_verified)

    def test_email_verification_rejects_already_verified_email(self):
        """Test that an already verified email cannot be verified again."""

        self.user.email_verified = True
        self.user.save(update_fields=['email_verified'])

        uid, token = self.get_verification_data()

        response = self.client.get(
            f'/api/verify-email/?uid={uid}&token={token}',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Email address is already verified.',
        )

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

    def test_user_cannot_assign_feed_item_to_another_user(self):
        """Test that feed items always belong to the authenticated user."""

        self.client.force_authenticate(user=self.user1)

        payload = {
            'user_profile': self.user2.id,
            'status_text': 'This should belong to User One',
        }

        response = self.client.post(
            '/api/feed/',
            payload,
        )

        self.assertEqual(response.status_code, 201)
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

class AdminPermissionTests(TestCase):
    """Tests for admin-only permissions."""

    def setUp(self):
        self.client = APIClient()

        self.admin = models.UserProfile.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='testpass123',
        )

        self.staff = models.UserProfile.objects.create_user(
            email='staff@example.com',
            name='Staff User',
            password='testpass123',
        )
        self.staff.is_staff = True
        self.staff.save()

        self.user = models.UserProfile.objects.create_user(
            email='user@example.com',
            name='Regular User',
            password='testpass123',
        )

    def test_admin_has_permission(self):
        """Test that admin users have admin permission."""

        self.client.force_authenticate(user=self.admin)

        request = self.client.get('/api/profile/')

        permission = permissions.IsAdmin()

        self.assertTrue(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

    def test_staff_does_not_have_admin_permission(self):
        """Test that staff users do not have admin permission."""

        self.client.force_authenticate(user=self.staff)

        request = self.client.get('/api/profile/')

        permission = permissions.IsAdmin()

        self.assertFalse(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

    def test_user_does_not_have_admin_permission(self):
        """Test that regular users do not have admin permission."""

        self.client.force_authenticate(user=self.user)

        request = self.client.get('/api/profile/')

        permission = permissions.IsAdmin()

        self.assertFalse(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

    def test_anonymous_does_not_have_admin_permission(self):
        """Test that anonymous users do not have admin permission."""

        request = self.client.get('/api/profile/')

        permission = permissions.IsAdmin()

        self.assertFalse(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

class StaffPermissionTests(TestCase):
    """Tests for staff permissions."""

    def setUp(self):
        self.client = APIClient()

        self.admin = models.UserProfile.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='testpass123',
        )

        self.staff = models.UserProfile.objects.create_user(
            email='staff@example.com',
            name='Staff User',
            password='testpass123',
        )
        self.staff.is_staff = True
        self.staff.save()

        self.user = models.UserProfile.objects.create_user(
            email='user@example.com',
            name='Regular User',
            password='testpass123',
        )

    def test_admin_has_staff_permission(self):
        """Test that admin users have staff permission."""

        self.client.force_authenticate(user=self.admin)

        request = self.client.get('/api/profile/')

        permission = permissions.IsStaff()

        self.assertTrue(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

    def test_staff_has_staff_permission(self):
        """Test that staff users have staff permission."""

        self.client.force_authenticate(user=self.staff)

        request = self.client.get('/api/profile/')

        permission = permissions.IsStaff()

        self.assertTrue(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

    def test_user_does_not_have_staff_permission(self):
        """Test that regular users do not have staff permission."""

        self.client.force_authenticate(user=self.user)

        request = self.client.get('/api/profile/')

        permission = permissions.IsStaff()

        self.assertFalse(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

    def test_anonymous_does_not_have_staff_permission(self):
        """Test that anonymous users do not have staff permission."""

        request = self.client.get('/api/profile/')

        permission = permissions.IsStaff()

        self.assertFalse(
            permission.has_permission(
                request.wsgi_request,
                None,
            )
        )

class ProfileObjectPermissionTests(TestCase):
    """Tests for profile object-level permissions."""

    def setUp(self):
        self.client = APIClient()

        self.admin = models.UserProfile.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='testpass123',
        )

        self.staff = models.UserProfile.objects.create_user(
            email='staff@example.com',
            name='HR Staff',
            password='testpass123',
        )
        self.staff.is_staff = True
        self.staff.save()

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

    def test_user_can_update_own_profile(self):
        """Test that a user can update their own profile."""

        self.client.force_authenticate(user=self.user1)

        payload = {
            'name': 'Updated User One',
        }

        response = self.client.patch(
            f'/api/profile/{self.user1.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated User One')

    def test_user_cannot_update_other_profile(self):
        """Test that a user cannot update another user's profile."""

        self.client.force_authenticate(user=self.user1)

        payload = {
            'name': 'Hacked User Two',
        }

        response = self.client.patch(
            f'/api/profile/{self.user2.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_update_other_profile(self):
        """Test that staff can update another user's profile."""

        self.client.force_authenticate(user=self.staff)

        payload = {
            'name': 'Updated By HR',
        }

        response = self.client.patch(
            f'/api/profile/{self.user1.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated By HR')

    def test_admin_can_update_other_profile(self):
        """Test that admin can update another user's profile."""

        self.client.force_authenticate(user=self.admin)

        payload = {
            'name': 'Updated By Admin',
        }

        response = self.client.patch(
            f'/api/profile/{self.user1.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated By Admin')

class AdminEndpointTests(TestCase):
    """Tests for admin-only endpoints."""

    def setUp(self):
        self.client = APIClient()

        self.admin = models.UserProfile.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='testpass123',
        )

        self.staff = models.UserProfile.objects.create_user(
            email='staff@example.com',
            name='HR Staff',
            password='testpass123',
        )
        self.staff.is_staff = True
        self.staff.save()

        self.user = models.UserProfile.objects.create_user(
            email='user@example.com',
            name='Regular User',
            password='testpass123',
        )

    def test_admin_can_access_admin_endpoint(self):
        """Test that admin users can access the admin endpoint."""

        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/profile/admin-users/')

        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_admin_endpoint(self):
        """Test that staff users cannot access the admin endpoint."""

        self.client.force_authenticate(user=self.staff)

        response = self.client.get('/api/profile/admin-users/')

        self.assertEqual(response.status_code, 403)

    def test_user_cannot_access_admin_endpoint(self):
        """Test that regular users cannot access the admin endpoint."""

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/profile/admin-users/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_access_admin_endpoint(self):
        """Test that anonymous users cannot access the admin endpoint."""

        response = self.client.get('/api/profile/admin-users/')

        self.assertEqual(response.status_code, 401)

class FeedObjectPermissionTests(TestCase):
    """Tests for feed object-level permissions."""

    def setUp(self):
        self.client = APIClient()

        self.admin = models.UserProfile.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='testpass123',
        )

        self.staff = models.UserProfile.objects.create_user(
            email='staff@example.com',
            name='HR Staff',
            password='testpass123',
        )
        self.staff.is_staff = True
        self.staff.save()

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

        self.feed_item = models.ProfileFeedItem.objects.create(
            user_profile=self.user1,
            status_text='Original post',
        )

    def test_user_can_update_own_post(self):
        """Test that a user can update their own post."""

        self.client.force_authenticate(user=self.user1)

        payload = {
            'status_text': 'Updated own post',
        }

        response = self.client.patch(
            f'/api/feed/{self.feed_item.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['status_text'],
            'Updated own post',
        )

    def test_user_cannot_update_other_post(self):
        """Test that a user cannot update another user's post."""

        self.client.force_authenticate(user=self.user2)

        payload = {
            'status_text': 'Hacked post',
        }

        response = self.client.patch(
            f'/api/feed/{self.feed_item.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_update_other_post(self):
        """Test that staff can update another user's post."""

        self.client.force_authenticate(user=self.staff)

        payload = {
            'status_text': 'Updated by HR',
        }

        response = self.client.patch(
            f'/api/feed/{self.feed_item.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['status_text'],
            'Updated by HR',
        )

    def test_admin_can_update_other_post(self):
        """Test that admin can update another user's post."""

        self.client.force_authenticate(user=self.admin)

        payload = {
            'status_text': 'Updated by Admin',
        }

        response = self.client.patch(
            f'/api/feed/{self.feed_item.id}/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['status_text'],
            'Updated by Admin',
        )

class PasswordChangeTests(TestCase):
    """Tests for changing the authenticated user's password."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='passwordchange@example.com',
            name='Password Change User',
            password='OldPassword123!',
        )

        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        """Test changing the password with a valid new password."""

        payload = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post('/api/password-change/', payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['detail'],
            'Password changed successfully.'
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('NewPassword123!')
        )
        self.assertFalse(
            self.user.check_password('OldPassword123!')
        )

    def test_change_password_rejects_weak_password(self):
        """Test that a weak new password is rejected."""

        payload = {
            'old_password': 'OldPassword123!',
            'new_password': '123',
            'new_password_confirm': '123',
        }

        response = self.client.post('/api/password-change/', payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)
        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('OldPassword123!')
        )
        self.assertFalse(
            self.user.check_password('123')
        )

    def test_change_password_rejects_mismatched_passwords(self):
        """Test that mismatched new passwords are rejected."""

        payload = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'DifferentPassword123!',
        }

        response = self.client.post('/api/password-change/', payload)

        self.assertEqual(response.status_code, 400)

    def test_change_password_rejects_incorrect_old_password(self):
        """Test that an incorrect old password is rejected."""

        payload = {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post('/api/password-change/', payload)

        self.assertEqual(response.status_code, 400)

    def test_change_password_creates_audit_and_security_event(self):
        """Test that a successful password change creates audit records."""

        payload = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post(
            '/api/password-change/',
            payload,
        )

        self.assertEqual(response.status_code, 200)

        audit_log = models.AuditLog.objects.get(
            user=self.user,
            action='PASSWORD_CHANGE',
        )

        security_event = models.SecurityEvent.objects.get(
            user=self.user,
            event_type='PASSWORD_CHANGED',
        )

        self.assertEqual(
            audit_log.details,
            'User changed their password.',
        )

        self.assertEqual(
            security_event.details,
            'User changed their password.',
        )

class PasswordResetTests(TestCase):
    """Tests for password reset confirmation."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='passwordreset@example.com',
            name='Password Reset User',
            password='OldPassword123!',
        )

    def test_password_reset_confirm_success(self):
        """Test resetting the password with a valid new password."""

        response = self.client.post(
            '/api/password-reset/',
            {'email': self.user.email},
        )

        self.assertEqual(response.status_code, 200)

        payload = {
            'uid': response.data['uid'],
            'token': response.data['token'],
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['detail'],
            'Password has been reset successfully.',
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('NewPassword123!')
        )
        self.assertFalse(
            self.user.check_password('OldPassword123!')
        )

    def test_password_reset_confirm_rejects_weak_password(self):
        """Test that a weak password is rejected."""

        response = self.client.post(
            '/api/password-reset/',
            {'email': self.user.email},
        )

        self.assertEqual(response.status_code, 200)

        payload = {
            'uid': response.data['uid'],
            'token': response.data['token'],
            'new_password': '123',
            'new_password_confirm': '123',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
        )

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('OldPassword123!')
        )
        self.assertFalse(
            self.user.check_password('123')
        )

    def test_password_reset_confirm_rejects_mismatched_passwords(self):
        """Test that mismatched passwords are rejected."""

        response = self.client.post(
            '/api/password-reset/',
            {'email': self.user.email},
        )

        self.assertEqual(response.status_code, 200)

        payload = {
            'uid': response.data['uid'],
            'token': response.data['token'],
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'DifferentPassword123!',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
        )

        self.assertEqual(response.status_code, 400)

    def test_password_reset_request_user_not_found(self):
        """Test password reset request for an unknown email."""

        response = self.client.post(
            '/api/password-reset/',
            {'email': 'doesnotexist@example.com'},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'No user found with this email address.',
        )

    def test_password_reset_confirm_invalid_uid(self):
        """Test password reset confirmation with an invalid UID."""

        payload = {
            'uid': 'invalid-uid',
            'token': 'invalid-token',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid password reset link.',
        )

    def test_password_reset_confirm_invalid_token(self):
        """Test password reset confirmation with an invalid token."""

        response = self.client.post(
            '/api/password-reset/',
            {'email': self.user.email},
        )

        self.assertEqual(response.status_code, 200)

        payload = {
            'uid': response.data['uid'],
            'token': 'invalid-token',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid or expired password reset token.',
        )

class PasswordResetErrorTests(TestCase):
    """Tests for password reset error handling."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='reseterror@example.com',
            name='Reset Error User',
            password='OldPassword123!',
        )

    def test_password_reset_rejects_unknown_email(self):
        """Test that an unknown email returns a 404 response."""

        response = self.client.post(
            '/api/password-reset/',
            {
                'email': 'doesnotexist@example.com',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'No user found with this email address.',
        )

    def test_password_reset_confirm_rejects_invalid_uid(self):
        """Test that an invalid UID is rejected."""

        payload = {
            'uid': 'invalid-uid',
            'token': 'invalid-token',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid password reset link.',
        )

    def test_password_reset_confirm_rejects_invalid_token(self):
        """Test that an invalid reset token is rejected."""

        uid = urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

        payload = {
            'uid': uid,
            'token': 'invalid-token',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!',
        }

        response = self.client.post(
            '/api/password-reset-confirm/',
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid or expired password reset token.',
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('OldPassword123!')
        )

class LoginAuditTests(TestCase):
    """Tests audit logging for successful and failed logins."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='auditlogin@example.com',
            name='Audit Login User',
            password='LoginPassword123!',
        )

    def test_successful_login_creates_audit_and_security_event(self):
        """Test that a successful login creates audit records."""

        response = self.client.post(
            '/api/login/',
            {
                'email': 'auditlogin@example.com',
                'password': 'LoginPassword123!',
            },
        )

        self.assertEqual(response.status_code, 200)

        audit_log = models.AuditLog.objects.get(
            user=self.user,
            action='LOGIN',
        )

        security_event = models.SecurityEvent.objects.get(
            user=self.user,
            event_type='LOGIN_SUCCESS',
        )

        self.assertEqual(
            audit_log.details,
            'User logged in successfully.',
        )
        self.assertEqual(
            security_event.details,
            'User logged in successfully.',
        )

    def test_failed_login_creates_security_events(self):
        """Test that a failed login creates audit and security events."""

        response = self.client.post(
            '/api/login/',
            {
                'email': self.user.email,
                'password': 'WrongPassword123!',
            },
        )

        self.assertEqual(response.status_code, 400)

        audit_log = models.AuditLog.objects.filter(
            action='LOGIN_FAILED'
        ).first()

        security_event = models.SecurityEvent.objects.filter(
            event_type='LOGIN_FAILED'
        ).first()

        self.assertIsNotNone(audit_log)
        self.assertIsNotNone(security_event)

        self.assertIsNone(audit_log.user)
        self.assertIsNone(security_event.user)

        self.assertEqual(
            audit_log.details,
            'Failed login attempt.',
        )

        self.assertEqual(
            security_event.details,
            'Failed login attempt.',
        )

class AccountStatusAuditTests(TestCase):
    """Tests audit logging for account activation and deactivation."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='accountaudit@example.com',
            name='Account Audit User',
            password='AccountPassword123!',
        )

        self.staff_user = models.UserProfile.objects.create_user(
            email='staffaudit@example.com',
            name='Staff Audit User',
            password='StaffPassword123!',
        )

        self.staff_user.is_staff = True
        self.staff_user.save(update_fields=['is_staff'])

        self.client.force_authenticate(user=self.staff_user)
    def test_account_status_returns_404_for_unknown_user(self):
        """Test that an unknown user returns a 404 response."""

        response = self.client.patch(
            '/api/account-status/999999/',
            {'is_active': False},
            format='json',
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'],
            'User not found.',
        )
    def test_activate_account_creates_audit_and_security_event(self):
        """Test that activating an account creates audit records."""

        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        response = self.client.patch(
            f'/api/account-status/{self.user.id}/',
            {'is_active': True},
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        audit_log = models.AuditLog.objects.get(
            user=self.user,
            action='ACCOUNT_ACTIVATED',
        )

        security_event = models.SecurityEvent.objects.get(
            user=self.user,
            event_type='ACCOUNT_ACTIVATED',
        )

        self.assertEqual(
            audit_log.details,
            'User account was activated.',
        )

        self.assertEqual(
            security_event.details,
            'User account was activated.',
        )

    def test_deactivate_account_creates_audit_and_security_event(self):
        """Test that deactivating an account creates audit records."""

        response = self.client.patch(
            f'/api/account-status/{self.user.id}/',
            {'is_active': False},
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        audit_log = models.AuditLog.objects.get(
            user=self.user,
            action='ACCOUNT_DEACTIVATED',
        )

        security_event = models.SecurityEvent.objects.get(
            user=self.user,
            event_type='ACCOUNT_DEACTIVATED',
        )

        self.assertEqual(
            audit_log.details,
            'User account was deactivated.',
        )

        self.assertEqual(
            security_event.details,
            'User account was deactivated.',
        )


class UnauthorizedAccessAuditTests(TestCase):
    """Tests audit logging for unauthorized access attempts."""

    def setUp(self):
        self.client = APIClient()

        self.user1 = models.UserProfile.objects.create_user(
            email='unauthorized1@example.com',
            name='Unauthorized User One',
            password='Password123!',
        )

        self.user2 = models.UserProfile.objects.create_user(
            email='unauthorized2@example.com',
            name='Unauthorized User Two',
            password='Password123!',
        )

        self.client.force_authenticate(user=self.user1)

    def test_unauthorized_profile_update_creates_security_event(self):
        """Test that unauthorized profile access is logged."""

        response = self.client.patch(
            f'/api/profile/{self.user2.id}/',
            {'name': 'Unauthorized Update'},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

        audit_log = models.AuditLog.objects.get(
            user=self.user1,
            action='UNAUTHORIZED_ACCESS',
        )

        security_event = models.SecurityEvent.objects.get(
            user=self.user1,
            event_type='UNAUTHORIZED_ACCESS',
        )

        self.assertIn(
            f'/api/profile/{self.user2.id}/',
            audit_log.details,
        )

        self.assertIn(
            f'/api/profile/{self.user2.id}/',
            security_event.details,
        )

        self.user2.refresh_from_db()

        self.assertEqual(
            self.user2.name,
            'Unauthorized User Two',
        )

class LogoutTests(TestCase):
    """Tests for user logout and refresh-token blacklisting."""

    def setUp(self):
        self.client = APIClient()

        self.user = models.UserProfile.objects.create_user(
            email='logout@example.com',
            name='Logout User',
            password='LogoutPassword123!',
        )

    def test_logout_requires_refresh_token(self):
        """Test that logout requires a refresh token."""

        response = self.client.post(
            '/api/logout/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Refresh token is required.',
        )

    def test_logout_rejects_invalid_refresh_token(self):
        """Test that an invalid refresh token is rejected."""

        response = self.client.post(
            '/api/logout/',
            {'refresh': 'invalid-refresh-token'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['detail'],
            'Invalid or expired refresh token.',
        )

    def test_logout_blacklists_valid_refresh_token(self):
        """Test that a valid refresh token is blacklisted."""

        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            '/api/logout/',
            {'refresh': str(refresh)},
            format='json',
        )

        self.assertEqual(response.status_code, 205)
        self.assertEqual(
            response.data['detail'],
            'Successfully logged out.',
        )

        with self.assertRaises(TokenError):
            RefreshToken(str(refresh))

class AuditSecurityModelChoiceTests(TestCase):
    """Tests for audit log and security event choices."""

    def test_audit_log_choices_include_used_actions(self):
        """Test that AuditLog choices match actions used by the API."""

        choices = dict(models.AuditLog.ACTION_CHOICES)

        self.assertIn('LOGIN', choices)
        self.assertIn('LOGIN_FAILED', choices)
        self.assertIn('PASSWORD_CHANGE', choices)
        self.assertIn('ACCOUNT_ACTIVATED', choices)
        self.assertIn('ACCOUNT_DEACTIVATED', choices)
        self.assertIn('ACCOUNT_CHANGE', choices)
        self.assertIn('UNAUTHORIZED_ACCESS', choices)

    def test_security_event_choices_include_used_event_types(self):
        """Test that SecurityEvent choices match events used by the API."""

        event_types = dict(models.SecurityEvent.EVENT_TYPES)

        self.assertIn('LOGIN_SUCCESS', event_types)
        self.assertIn('LOGIN_FAILED', event_types)
        self.assertIn('PASSWORD_CHANGED', event_types)
        self.assertIn('ACCOUNT_ACTIVATED', event_types)
        self.assertIn('ACCOUNT_DEACTIVATED', event_types)
        self.assertIn('ACCOUNT_CHANGE', event_types)
        self.assertIn('UNAUTHORIZED_ACCESS', event_types)
