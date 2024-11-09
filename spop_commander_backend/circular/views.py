from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
import uuid

from circular.models import Circular, CircularAcknowledgment, CircularAttachment
from circular.serializers import CircularSerializer, CircularAcknowledgmentSerializer, CircularAttachmentSerializer


class CircularViewSet(viewsets.ModelViewSet):
    queryset = Circular.objects.all()
    serializer_class = CircularSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            id=uuid.uuid4(),
            created_by=self.request.user
        )

    def get_queryset(self):
        user = self.request.user
        return Circular.objects.filter(
            target_officers=user,
            is_deleted=False
        )

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        circular = self.get_object()
        if circular.has_officer_read(request.user.id):
            return Response(
                {'detail': 'Already acknowledged'},
                status=status.HTTP_400_BAD_REQUEST
            )

        acknowledgment = CircularAcknowledgment.objects.create(
            circular=circular,
            officer=request.user,
            device_info=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=request.META.get('REMOTE_ADDR', ''),
            location=request.data.get('location', '')
        )

        return Response(
            CircularAcknowledgmentSerializer(acknowledgment).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        circular = self.get_object()
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response(
                {'detail': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attachment = CircularAttachment.objects.create(
            id=uuid.uuid4(),
            circular=circular,
            file_name=file_obj.name,
            file_type=file_obj.content_type,
            file_size=file_obj.size,
            file_path=file_obj
        )

        return Response(
            CircularAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED
        )