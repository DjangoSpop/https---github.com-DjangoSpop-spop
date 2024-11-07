from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from core.permissions import IsCommanderOrReadOnly
from .models import Order, OrderAcknowledgment
from .serializers import OrderSerializer, OrderAcknowledgmentSerializer



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCommanderOrReadOnly]
    filterset_fields = ['status', 'priority', 'is_urgent']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        queryset = Order.objects.all()
        if not self.request.user.is_commander:
            queryset = queryset.filter(assigned_to=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        order = self.get_object()
        if not order.acknowledgment_required:
            return Response(
                {'error': 'Acknowledgment not required for this order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comments = request.data.get('comments', '')

        acknowledgment = OrderAcknowledgment.objects.create(
            order=order,
            user=request.user,
            comments=comments
        )

        order.acknowledged_at = timezone.now()
        order.save()

        return Response(OrderAcknowledgmentSerializer(acknowledgment).data)

    @action(detail=True, methods=['post'])
    def mark_urgent(self, request, pk=None):
        if not request.user.is_commander:
            return Response(
                {'error': 'Only commanders can mark orders as urgent'},
                status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        order.is_urgent = True
        order.priority = 'urgent'
        order.save()

        return Response(OrderSerializer(order).data)

    @action(detail=False)
    def urgent(self, request):
        urgent_orders = self.get_queryset().filter(is_urgent=True)
        serializer = self.get_serializer(urgent_orders, many=True)
        return Response(serializer.data)
