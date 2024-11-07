from django.shortcuts import render

# Create your views here.
# weekly_plans/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError
from .models import WeeklyPlan
from .serializers import WeeklyPlanSerializer

class WeeklyPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WeeklyPlanSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = WeeklyPlan.objects.filter(is_active=True)
        plan_type = self.request.query_params.get('plan_type', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if plan_type:
            queryset = queryset.filter(plan_type=plan_type)
        if start_date:
            queryset = queryset.filter(week_start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(week_end_date__lte=end_date)

        return queryset

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )