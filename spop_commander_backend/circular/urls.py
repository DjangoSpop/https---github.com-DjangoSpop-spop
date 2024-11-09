from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CircularViewSet

router = DefaultRouter()
router.register(r'circulars', CircularViewSet)

urlpatterns = [
    path('', include(router.urls)),
]