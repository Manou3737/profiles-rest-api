from django.test import TestCase
from rest_framework.test import APIClient

from . import models
from . import permissions

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
            'Password has been reset successfully.'
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
