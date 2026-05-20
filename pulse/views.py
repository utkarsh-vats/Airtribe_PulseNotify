from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.db.models import Count, Q
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, LoginSerializer, PriceAlertSerializer, AirportSerializer
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PriceAlert, NotificationLog, Airport
from .permissions import IsAdminUser
from .mock_data import AIRPORT_CODES
from .services import PriceService
from rest_framework.pagination import PageNumberPagination

price_service = PriceService()

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
    try:
        origin, destination = route.split('-')
    except ValueError:
        return JsonResponse({'error': 'Invalid route format.'}, status=status.HTTP_400_BAD_REQUEST)
    if origin not in AIRPORT_CODES or destination not in AIRPORT_CODES:
        return JsonResponse({'error': 'Invalid route.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        price = price_service.get_price(origin, destination)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not price:
        return JsonResponse({'error': 'Price not found.'}, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse(
        {
            'route': route,
            'price': price,
            'origin': f"{origin}: {AIRPORT_CODES.get(origin, '')}",
            'destination': f"{destination}: {AIRPORT_CODES.get(destination, '')}"
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
    
class AirportPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = []
    
    http_method_names = ['get']
    pagination_class = AirportPagination
    serializer_class = AirportSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Airport.objects.all().order_by("code")
        country = self.request.query_params.get("country")
        city = self.request.query_params.get("city")
        name = self.request.query_params.get("name")
        search = self.request.query_params.get("search")
        
        
        if country:
            queryset = queryset.filter(country__icontains=country)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if name:
            queryset = queryset.filter(name__icontains=name)

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(city__icontains=search) |
                Q(country__icontains=search)
            )

        return queryset


