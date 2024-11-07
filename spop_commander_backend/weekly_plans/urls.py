# weekly_plans/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WeeklyPlanViewSet

router = DefaultRouter()
router.register(r'weekly-plans', WeeklyPlanViewSet, basename='weekly-plan')

urlpatterns = [
    path('', include(router.urls)),
]