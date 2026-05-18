from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.db.models import Count
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, LoginSerializer, PriceAlertSerializer
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PriceAlert, NotificationLog
import random
from .permissions import IsAdminUser
from .mock_data import MOCK_PRICES, AIRPORT_CODES

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data.get('email', None)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        token = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'access': str(token.access_token),
            'role': user.profile.role if hasattr(user, 'profile') else None     # type: ignore
        }, status=status.HTTP_201_CREATED)
    
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request, username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        token = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'access': str(token.access_token),
            'refresh': str(token)
        }, status=status.HTTP_200_OK)

class AlertViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    serializer_class = PriceAlertSerializer

    def get_queryset(self) -> QuerySet:
        return PriceAlert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs) -> Response:
        alert = self.get_object()
        alert.status = PriceAlert.Status.INACTIVE
        alert.save()
        return Response({"status": "inactive"}, status=status.HTTP_200_OK)
    
def flight_price(request) -> JsonResponse:
    route = request.GET.get('route', '')
    price_range = MOCK_PRICES.get(route)
    if not price_range:
        return JsonResponse({'error': 'Route not found.'}, status=status.HTTP_404_NOT_FOUND)
    price = random.randint(*price_range)
    return JsonResponse(
        {
            'route': route,
            'price': price,
            'origin': AIRPORT_CODES.get(route.split('-')[0], ""),
            'destination': AIRPORT_CODES.get(route.split('-')[1], "")
        }, 
        status=status.HTTP_200_OK
    )

class AdminSummaryView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        total_alerts = PriceAlert.objects.count()
        active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE).count()
        triggered_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.TRIGGERED).count()
        total_notifications = NotificationLog.objects.count()
        top_routes = PriceAlert.objects.values('origin', 'destination').annotate(alert_count=Count('id')).order_by('-alert_count')
        top_routes_data = [
            {
                'route': f"{route['origin']}-{route['destination']}",
                'alert_count': route['alert_count']
            }
            for route in top_routes
        ]
        return Response({
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'triggered_alerts': triggered_alerts,
            'total_notifications': total_notifications,
            'top_routes': top_routes_data
        }, status=status.HTTP_200_OK)
    

