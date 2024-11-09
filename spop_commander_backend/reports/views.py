from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from reports.models import Reports, ReportAttachment, ReportStatistics, ReportStatus
from reports.serializers import ReportSerializer, ReportAttachmentSerializer, ReportStatisticsSerializer


# Create your views here.
class ReportsViewSet(viewsets.ModelViewSet):
    queryset = Reports.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Reports.objects.filter(officer=user)

    def perform_create(self, serializer):
        serializer.save(officer=self.request.user, submitted_at=timezone.now())

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        report = self.get_object()
        decision = request.data.get("decision")
        feedback = request.data.get("feedback", "")
        awards_points = request.data.get("awards_points", 0)

        report.status = decision
        report.feedback = feedback
        report.awards_points = awards_points
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()

        return Response({"status": "Report reviewed successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def submit_revision(self, request, pk=None):
        report = self.get_object()
        report.status = ReportStatus.PENDING
        report.feedback = request.data.get("feedback", "")
        report.save()
        return Response({"status": "Revision submitted successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        report = self.get_object()
        report.status = ReportStatus.ARCHIVED
        report.save()
        return Response({"status": "Report archived successfully"}, status=status.HTTP_200_OK)


class ReportAttachmentViewSet(viewsets.ModelViewSet):
    queryset = ReportAttachment.objects.all()
    serializer_class = ReportAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportStatistics.objects.all()
    serializer_class = ReportStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def officer_statistics(self, request):
        officer = request.user
        stats, created = ReportStatistics.objects.get_or_create(officer=officer)
        serializer = self.get_serializer(stats)
        return Response(serializer.data)