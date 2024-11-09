from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from authentication.views import UserViewSet
from circular.views import CircularViewSet
from officers.views import OfficerViewSet
from order.views import OrderViewSet
from reports.views import ReportsViewSet
from spop_commander_backend import settings
from sync.views import SyncViewSet
from tasks.views import TaskViewSet
from weekly_plans.views import WeeklyPlanViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="SPOP Commander API",
        default_version='v1',
        description="API Documentation for SPOP Commander",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=settings.API_URL if hasattr(settings, 'API_URL') else None,
)

router = DefaultRouter()
router.register(r'auth', UserViewSet, basename='auth')
router.register(r'officers', OfficerViewSet, basename='officer')
router.register(r'sync', SyncViewSet, basename='sync')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'weeklyplan', WeeklyPlanViewSet, basename='weekly-plan')
router.register(r'reports' , ReportsViewSet, basename='reports')
router.register(r'circulars', CircularViewSet, basename='circulars')



urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Get access and refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh access token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    # Include all API URLs from the app
]