# dashboard/management/commands/generate_mock_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from faker import Faker
from officers.models import Officer
from tasks.models import Task
from order.models import Order
from dashboard.models import (
    DashboardMetric,
    PerformanceSnapshot,
    Activity
)


class Command(BaseCommand):
    help = 'Generate mock data for testing'

    def __init__(self):
        super().__init__()
        self.fake = Faker('ar')
        self.officer_ranks = ['ملازم', 'ملازم أول', 'نقيب', 'رائد', 'مقدم', 'عقيد']
        self.task_priorities = ['low', 'medium', 'high', 'urgent']
        self.task_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        self.officer_statuses = ['available', 'on_mission', 'on_leave']

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating mock data...')

        # Create test users
        self.create_users()

        # Create officers
        officers = self.create_officers()

        # Create tasks and orders
        self.create_tasks(officers)
        self.create_orders(officers)

        # Generate dashboard data
        self.generate_dashboard_data()

        self.stdout.write(self.style.SUCCESS('Successfully generated mock data'))

    def create_users(self):
        # Create admin user
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        # Create test users
        for i in range(5):
            username = f'user{i}'
            User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='test123'
            )

    def create_officers(self):
        officers = []
        for _ in range(10):
            officer = Officer.objects.create(
                name=self.fake.name(),
                rank=random.choice(self.officer_ranks),
                status=random.choice(self.officer_statuses),
                phone_number=self.fake.phone_number(),
                specializations=['تدريب', 'أمن', 'عمليات'],
                photo='default.jpg'
            )
            officers.append(officer)
        return officers

    def create_tasks(self, officers):
        for _ in range(20):
            start_date = timezone.now() - timedelta(days=random.randint(0, 30))
            due_date = start_date + timedelta(days=random.randint(1, 14))

            Task.objects.create(
                title=self.fake.sentence(),
                description=self.fake.paragraph(),
                assigned_to=random.choice(officers),
                start_date=start_date,
                due_date=due_date,
                status=random.choice(self.task_statuses),
                priority=random.choice(self.task_priorities),
                completion_rate=random.uniform(0, 100)
            )

    def create_orders(self, officers):
        for _ in range(15):
            is_urgent = random.choice([True, False])
            Order.objects.create(
                title=self.fake.sentence(),
                description=self.fake.paragraph(),
                priority='urgent' if is_urgent else random.choice(['high', 'normal']),
                status=random.choice(['pending', 'in_progress', 'completed']),
                assigned_to=random.choice(officers),
                due_date=timezone.now() + timedelta(days=random.randint(1, 7)),
                is_urgent=is_urgent
            )

    def generate_dashboard_data(self):
        # Generate performance snapshots for the last 30 days
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            PerformanceSnapshot.objects.create(
                date=date,
                total_officers=random.randint(8, 12),
                available_officers=random.randint(4, 8),
                on_mission_officers=random.randint(2, 4),
                on_leave_officers=random.randint(0, 2),
                total_tasks=random.randint(15, 25),
                pending_tasks=random.randint(5, 10),
                in_progress_tasks=random.randint(3, 8),
                completed_tasks=random.randint(5, 15),
                overdue_tasks=random.randint(0, 3),
                completion_rate=random.uniform(60, 95),
                avg_response_time=random.uniform(1, 24)
            )

        # Generate metrics
        metric_types = ['task_completion', 'officer_availability', 'response_time']
        categories = ['performance', 'efficiency', 'workload']

        for _ in range(50):
            DashboardMetric.objects.create(
                metric_type=random.choice(metric_types),
                metric_value=random.uniform(0, 100),
                metric_label=self.fake.word(),
                category=random.choice(categories),
                timestamp=timezone.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )
            )

        # Generate activities
        activity_types = ['task', 'order', 'officer', 'system']
        for _ in range(100):
            Activity.objects.create(
                activity_type=random.choice(activity_types),
                title=self.fake.sentence(),
                description=self.fake.paragraph(),
                status=random.choice(['created', 'updated', 'completed']),
                timestamp=timezone.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
            )