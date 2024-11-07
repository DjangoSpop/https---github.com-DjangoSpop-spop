# orders/tests/test_models.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from orders.models import Order


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='commander',
            password='testpass123',
            is_commander=True
        )
        self.client.force_authenticate(user=self.user)

        self.officer = Officer.objects.create(
            name='Test Officer',
            rank='Lieutenant',
            phone_number='1234567890'
        )

        self.order_data = {
            'title': 'Test Order',
            'description': 'Test Description',
            'assigned_to': self.officer.id,
            'priority': 'high',
            'due_date': '2024-02-01T12:00:00Z'
        }

    def test_create_order(self):
        url = reverse('order-list')
        response = self.client.post(url, self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_mark_urgent(self):
        order = Order.objects.create(**self.order_data)
        url = reverse('order-mark-urgent', kwargs={'pk': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Order.objects.get(id=order.id).is_urgent)