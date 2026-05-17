from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alerts')

urlpatterns = [
    *router.urls,
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('flights/price/', flight_price, name='flight_price')
]