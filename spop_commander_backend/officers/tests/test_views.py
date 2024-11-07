from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from authentication.models import User
from officers.models import Officer


class OfficerTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_commander=True
        )
        self.client.force_authenticate(user=self.user)

        # Test data for creating an officer
        self.test_user = User.objects.create_user(
            username='officer1',
            password='officer123',
            email='officer1@example.com'
        )

        self.officer_data = {
            'user': self.test_user.id,
            'name': 'Test Officer',
            'rank': 'Lieutenant',
            'phone_number': '1234567890',
            'status': 'available'
        }

    def test_create_officer(self):
        url = reverse('officer-list')
        response = self.client.post(url, self.officer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Officer.objects.count(), 1)
        self.assertEqual(Officer.objects.get().name, 'Test Officer')

    def test_list_officers(self):
        # Create an officer first
        Officer.objects.create(
            user=self.test_user,
            name='Test Officer',
            rank='Lieutenant',
            phone_number='1234567890'
        )

        url = reverse('officer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_officer(self):
        # Create an officer first
        officer = Officer.objects.create(
            user=self.test_user,
            name='Test Officer',
            rank='Lieutenant',
            phone_number='1234567890'
        )

        url = reverse('officer-detail', kwargs={'pk': officer.id})
        updated_data = {
            'user': self.test_user.id,
            'name': 'Updated Officer',
            'rank': 'Captain',
            'phone_number': '0987654321',
            'status': 'on_mission'
        }

        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Officer.objects.get().name, 'Updated Officer')