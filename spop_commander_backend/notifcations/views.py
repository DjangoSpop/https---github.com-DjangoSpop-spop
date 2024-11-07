from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from .pagination import NotificationPagination


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Filter by type if specified
        notification_type = request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(type=notification_type)

        # Filter by read status if specified
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            if is_read:
                queryset = queryset.exclude(read_at=None)
            else:
                queryset = queryset.filter(read_at=None)

        # Filter by priority if specified
        priority = request.query_params.get('priority')
        if priority is not None:
            queryset = queryset.filter(priority=priority)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().filter(read_at=None).update(
            read_at=timezone.now()
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_unread()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(read_at=None).count()
        return Response({'count': count})


class NotificationPreferenceViewSet(mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    viewsets.GenericViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return NotificationPreference.objects.get_or_create(
            user=self.request.user
        )[0]
