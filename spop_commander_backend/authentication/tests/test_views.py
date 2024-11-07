from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.me_url = reverse('user-me')
        self.update_profile_url = reverse('user-update-profile')
        self.token_url = reverse('token_obtain_pair')

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '1234567890',
            'rank': 'lieutenant'
        }

    def create_and_login_user(self, **kwargs):
        """Helper method to create and login a user"""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            **kwargs
        }
        user = User.objects.create_user(**user_data)
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return user

    def test_register_user(self):
        """Test user registration"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertNotIn('password', response.data)

    def test_me_endpoint(self):
        """Test getting current user profile"""
        user = self.create_and_login_user()

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)

    def test_update_profile(self):
        """Test updating user profile"""
        user = self.create_and_login_user()

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '9876543210'
        }

        response = self.client.patch(
            self.update_profile_url,
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, update_data['first_name'])
        self.assertEqual(user.last_name, update_data['last_name'])
        self.assertEqual(user.phone_number, update_data['phone_number'])

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Try accessing me endpoint without authentication
        self.client.credentials()  # Clear credentials
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_validation(self):
        """Test validation during profile update"""
        user = self.create_and_login_user()

        # Test invalid email format
        response = self.client.patch(
            self.update_profile_url,
            {'email': 'invalid-email'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_validation(self):
        """Test validation during registration"""
        # Test missing required fields
        invalid_data = self.user_data.copy()
        del invalid_data['password']

        response = self.client.post(
            self.register_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create first user
        self.client.post(self.register_url, self.user_data, format='json')

        # Try to create second user with same username
        response = self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_password_change(self):
        """Test password change functionality"""
        user = self.create_and_login_user()

        response = self.client.post(
            reverse('user-change-password'),
            {
                'old_password': 'TestPass123!',
                'new_password': 'NewTestPass123!',
                'confirm_password': 'NewTestPass123!'
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify can login with new password
        login_response = self.client.post(
            self.token_url,
            {
                'username': user.username,
                'password': 'NewTestPass123!'
            },
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)


