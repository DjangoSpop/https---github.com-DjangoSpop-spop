from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from authentication.serializers import User
from tasks.models import Task
from officers.models import Officer
from datetime import datetime, timedelta


class TaskViewSetTests(APITestCase):
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

        self.test_task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'assigned_to': self.officer.id,
            'priority': 'high',
            'status': 'pending',
            'start_date': datetime.now().isoformat(),
            'due_date': (datetime.now() + timedelta(days=1)).isoformat()
        }

    def test_create_task(self):
        url = reverse('task-list')
        response = self.client.post(url, self.test_task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_task_status(self):
        task = Task.objects.create(**self.test_task_data)
        url = reverse('task-update-task-status', kwargs={'pk': task.id})

        response = self.client.post(url, {'status': 'in_progress'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get().status, 'in_progress')