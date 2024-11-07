from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from authentication.serializers import User


class SyncTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='commander',
            password='testpass123',
            is_commander=True
        )
        self.client.force_authenticate(user=self.user)

    def test_sync_pull(self):
        url = reverse('sync-pull')
        response = self.client.post(url, {
            'last_sync': '2024-01-01T00:00:00Z',
            'entity_types': ['tasks', 'orders']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sync_push(self):
        url = reverse('sync-push')
        response = self.client.post(url, {
            'changes': {
                'tasks': [],
                'orders': []
            }
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)