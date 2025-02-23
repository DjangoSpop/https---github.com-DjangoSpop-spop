from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from tasks.models import Task
from tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


    def get_queryset(self):
        """Override get_queryset to allow filtering based on query parameters."""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        officer_id = self.request.query_params.get('officer_id')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority:
            queryset = queryset.filter(priority=priority)
        if officer_id:
            queryset = queryset.filter(assigned_to_id=officer_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new task associated with the current user."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def active(self, request):
        tasks = Task.objects.filter(
            assigned_to=request.user.officer_profile,
            status='in_progress'
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        tasks = Task.objects.filter(status='pending')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['patch'])
    def update_task_status(self, request, pk=None):
        """Update the status of a specific task by its primary key."""
        task = self.get_object()
        new_status = request.data.get('status')

        if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save()
        return Response({'status': task.status}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get a list of active tasks with 'in_progress' status."""
        active_tasks = self.get_queryset().filter(status='in_progress')
        serializer = self.get_serializer(active_tasks, many=True)
        return Response(serializer.data)
