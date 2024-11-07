# officers/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F
from datetime import datetime, timedelta

from .models import Officer
from .serializers import OfficerSerializer, OfficerDetailSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer


class OfficerViewSet(viewsets.ModelViewSet):
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'details']:
            return OfficerDetailSerializer
        return OfficerSerializer

    def get_queryset(self):
        queryset = Officer.objects.all()

        # Filter by status if provided
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        # Filter by availability
        available = self.request.query_params.get('available', None)
        if available:
            queryset = queryset.filter(status='available')

        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(rank__icontains=search) |
                Q(phone_number__icontains=search)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new officer"""
        try:
            # Add user to request data if not present
            if not request.data.get('user'):
                request.data['user'] = request.user.id

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            officer = serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_officers = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_officers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_officers = self.queryset.filter(status='available')
        serializer = self.get_serializer(available_officers, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        status_filter = request.query_params.get('status', None)
        queryset = self.queryset
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update officer status"""
        officer = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['available', 'active', 'on_mission', 'on_leave']:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        officer.status = new_status
        officer.save()

        serializer = self.get_serializer(officer)
        return Response(serializer.data)
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update officer status"""
        officer = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in [choice[0] for choice in Officer.STATUS_CHOICES]:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        officer.status = new_status
        officer.save()

        return Response(
            self.get_serializer(officer).data
        )

    @action(detail=True)
    def tasks(self, request, pk=None):
        """Get officer's tasks"""
        officer = self.get_object()
        tasks = Task.objects.filter(assigned_officer=officer)

        # Filter by status if provided
        task_status = request.query_params.get('status', None)
        if task_status:
            tasks = tasks.filter(status=task_status)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def performance(self, request, pk=None):
        """Get officer's performance metrics"""
        officer = self.get_object()
        period = request.query_params.get('period', '30')  # Default to 30 days

        try:
            days = int(period)
            start_date = datetime.now() - timedelta(days=days)

            # Get tasks in period
            tasks = Task.objects.filter(
                assigned_officer=officer,
                created_at__gte=start_date
            )

            # Calculate metrics
            total_tasks = tasks.count()
            completed_tasks = tasks.filter(status='completed').count()
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # Average response time calculation
            response_times = tasks.exclude(
                started_at__isnull=True
            ).annotate(
                response_time=(F('started_at') - F('created_at'))
            ).values_list('response_time', flat=True)

            avg_response_time = sum(
                [rt.total_seconds() for rt in response_times]
            ) / len(response_times) if response_times else 0

            return Response({
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': completion_rate,
                'average_response_time': avg_response_time,
                'period_days': days
            })

        except ValueError:
            return Response(
                {'error': 'Invalid period parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True)
    def task_history(self, request, pk=None):
        """Get officer's task history"""
        officer = self.get_object()
        tasks = Task.objects.filter(
            assigned_officer=officer,
            status__in=['completed', 'cancelled']
        ).order_by('-completed_at')

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def statistics(self, request):
        """Get overall officer statistics"""
        total_officers = Officer.objects.count()
        available_officers = Officer.objects.filter(status='available').count()
        on_mission = Officer.objects.filter(status='on_mission').count()
        on_leave = Officer.objects.filter(status='on_leave').count()

        return Response({
            'total': total_officers,
            'available': available_officers,
            'on_mission': on_mission,
            'on_leave': on_leave
        })

    def perform_destroy(self, instance):
        """Override delete to handle constraints"""
        # Check if officer has ongoing tasks
        if instance.assigned_tasks.exclude(status__in=['completed', 'cancelled']).exists():
            raise ValidationError('Cannot delete officer with ongoing tasks')
        instance.delete()