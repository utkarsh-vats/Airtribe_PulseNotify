from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path
from .views import *

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alerts')

urlpatterns = [
    *router.urls,
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('flights/price/', flight_price, name='flight_price'),
    path('admin/summary/', AdminSummaryView.as_view(), name='summary'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]