# officers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfficerViewSet

router = DefaultRouter()
router.register(r'officers', OfficerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]