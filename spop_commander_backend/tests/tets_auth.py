# tests/test_auth.py
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

class AuthTests(APITestCase):
    def test_register(self):
        url = reverse('auth-register')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        url = reverse('auth-login')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        url = reverse('auth-logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_validate_token(self):
        url = reverse('auth-validate-token')
        data = {'token': 'some_valid_token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
