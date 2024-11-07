# dashboard/views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Sum, Avg, Max
from django.utils import timezone
from datetime import timedelta

from officers.models import Officer
from tasks.models import Task
from order.models import Order
from .serializers import DashboardSummarySerializer


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Get dashboard summary including:
        - Officers statistics
        - Tasks statistics
        - Orders statistics
        - Recent activities
        """
        try:
            # Get current date for calculations
            today = timezone.now()
            thirty_days_ago = today - timedelta(days=30)

            # Officers Statistics
            officers_stats = {
                'total_officers': Officer.objects.count(),
                'available_officers': Officer.objects.filter(status='available').count(),
                'on_mission_officers': Officer.objects.filter(status='on_mission').count(),
                'on_leave_officers': Officer.objects.filter(status='on_leave').count(),
            }

            # Tasks Statistics
            tasks_stats = {
                'total_tasks': Task.objects.count(),
                'pending_tasks': Task.objects.filter(status='pending').count(),
                'in_progress_tasks': Task.objects.filter(status='in_progress').count(),
                'completed_tasks': Task.objects.filter(status='completed').count(),
                'overdue_tasks': Task.objects.filter(
                    due_date__lt=today,
                    status__in=['pending', 'in_progress']
                ).count(),
                'completion_rate': self._calculate_completion_rate(),
            }

            # Orders Statistics
            orders_stats = {
                'total_orders': Order.objects.count(),
                'urgent_orders': Order.objects.filter(priority='urgent').count(),
                'pending_orders': Order.objects.filter(status='pending').count(),
                'recent_orders': Order.objects.filter(
                    created_at__gte=thirty_days_ago
                ).count(),
            }

            # Recent Activities
            recent_activities = self._get_recent_activities()

            # Performance Metrics
            performance_metrics = self._get_performance_metrics()

            # Compile summary data
            summary_data = {
                'officers': officers_stats,
                'tasks': tasks_stats,
                'orders': orders_stats,
                'recent_activities': recent_activities,
                'performance_metrics': performance_metrics,
                'last_updated': timezone.now(),
            }

            serializer = DashboardSummarySerializer(summary_data)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=500
            )

    def _calculate_completion_rate(self):
        """Calculate task completion rate for the last 30 days"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        completed = Task.objects.filter(
            status='completed',
            completion_date__gte=thirty_days_ago
        ).count()
        total = Task.objects.filter(
            created_at__gte=thirty_days_ago
        ).count()

        return (completed / total * 100) if total > 0 else 0

    def _get_recent_activities(self):
        """Get recent activities across tasks and orders"""
        today = timezone.now()
        seven_days_ago = today - timedelta(days=7)

        # Recent task updates
        recent_tasks = Task.objects.filter(
            updated_at__gte=seven_days_ago
        ).order_by('-updated_at')[:5].values(
            'id', 'title', 'status', 'updated_at', 'assigned_to__name'
        )

        # Recent order updates
        recent_orders = Order.objects.filter(
            updated_at__gte=seven_days_ago
        ).order_by('-updated_at')[:5].values(
            'id', 'title', 'status', 'updated_at', 'assigned_to__name'
        )

        # Combine and sort activities
        activities = []
        for task in recent_tasks:
            activities.append({
                'type': 'task',
                'id': task['id'],
                'title': task['title'],
                'status': task['status'],
                'timestamp': task['updated_at'],
                'officer': task['assigned_to__name'],
            })

        for order in recent_orders:
            activities.append({
                'type': 'order',
                'id': order['id'],
                'title': order['title'],
                'status': order['status'],
                'timestamp': order['updated_at'],
                'officer': order['assigned_to__name'],
            })

        return sorted(
            activities,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]

    def _get_performance_metrics(self):
        """Calculate performance metrics"""
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Task completion metrics
        task_metrics = Task.objects.filter(
            completion_date__gte=thirty_days_ago
        ).aggregate(
            avg_completion_time=Avg('completion_time'),
            total_completed=Count('id'),
            on_time_completion=Count(
                'id',
                filter=Q(completion_date__lte=F('due_date'))
            ),
        )

        # Officer performance metrics
        officer_metrics = Officer.objects.annotate(
            completed_tasks=Count(
                'assigned_tasks',
                filter=Q(
                    assigned_tasks__status='completed',
                    assigned_tasks__completion_date__gte=thirty_days_ago
                )
            ),
            total_tasks=Count(
                'assigned_tasks',
                filter=Q(assigned_tasks__created_at__gte=thirty_days_ago)
            ),
        ).aggregate(
            avg_tasks_per_officer=Avg('completed_tasks'),
            max_tasks_completed=Max('completed_tasks'),
        )

        return {
            'task_metrics': task_metrics,
            'officer_metrics': officer_metrics,
        }