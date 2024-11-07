
# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from officers.models import Officer
from officers.serializers import OfficerSerializer
from order.models import Order
from order.serializers import OrderSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer
from .models import SyncStatus, SyncQueue
from .serializers import SyncStatusSerializer, SyncQueueSerializer



class SyncViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def pull(self, request):
        last_sync = request.data.get('last_sync')
        entity_types = request.data.get('entity_types', [])

        try:
            last_sync_date = timezone.datetime.fromisoformat(last_sync)
        except (ValueError, TypeError):
            last_sync_date = timezone.now() - timezone.timedelta(days=30)

        updates = {
            'tasks': [],
            'orders': [],
            'officers': [],
        }

        # Get updated tasks
        if 'tasks' in entity_types:
            tasks = Task.objects.filter(updated_at__gt=last_sync_date)
            updates['tasks'] = TaskSerializer(tasks, many=True).data

        # Get updated orders
        if 'orders' in entity_types:
            orders = Order.objects.filter(updated_at__gt=last_sync_date)
            updates['orders'] = OrderSerializer(orders, many=True).data

        # Get updated officers
        if 'officers' in entity_types:
            officers = Officer.objects.filter(updated_at__gt=last_sync_date)
            updates['officers'] = OfficerSerializer(officers, many=True).data

        return Response({
            'last_sync': timezone.now().isoformat(),
            'updates': updates
        })

    @action(detail=False, methods=['post'])
    def push(self, request):
        changes = request.data.get('changes', {})

        processed = {
            'success': [],
            'failed': []
        }

        for entity_type, entities in changes.items():
            for entity_data in entities:
                try:
                    self._process_entity_change(entity_type, entity_data)
                    processed['success'].append({
                        'type': entity_type,
                        'id': entity_data.get('id')
                    })
                except Exception as e:
                    processed['failed'].append({
                        'type': entity_type,
                        'id': entity_data.get('id'),
                        'error': str(e)
                    })

        return Response(processed)

    def _process_entity_change(self, entity_type, data):
        model_map = {
            'tasks': Task,
            'orders': Order,
            'officers': Officer,
        }

        serializer_map = {
            'tasks': TaskSerializer,
            'orders': OrderSerializer,
            'officers': OfficerSerializer,
        }

        if entity_type not in model_map:
            raise ValueError(f'Unknown entity type: {entity_type}')

        model = model_map[entity_type]
        serializer_class = serializer_map[entity_type]

        if 'id' in data:
            instance = model.objects.get(id=data['id'])
            serializer = serializer_class(instance, data=data, partial=True)
        else:
            serializer = serializer_class(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
