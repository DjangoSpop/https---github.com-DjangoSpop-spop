from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from orders.models import Order
from datetime import datetime


class OrderViewSetTests(APITestCase):
    def setUp(self):
        self.commander = User.objects.create_user(
            username='commander',
            password='commander123',
            is_commander=True
        )

        self.client.force_authenticate(user=self.commander)

        self.officer = Officer.objects.create(
            name='Test Officer',
            rank='Lieutenant',
            phone_number='1234567890'
        )

        self.test_order_data = {
            'title': 'Test Order',
            'description': 'Test Description',
            'assigned_to': self.officer.id,
            'priority': 'high',
            'status': 'pending',
            'due_date': datetime.now().isoformat()
        }

    def test_create_order(self):
        url = reverse('order-list')
        response = self.client.post(url, self.test_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mark_urgent(self):
        order = Order.objects.create(**self.test_order_data)
        url = reverse('order-mark-urgent', kwargs={'pk': order.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Order.objects.get().is_urgent)