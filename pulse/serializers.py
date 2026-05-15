from rest_framework import serializers
from .models import UserProfile, PriceAlert, NotificationLog

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(required=False)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128, write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = ['id', 'user', 'origin', 'destination', 'threshold_price', 'status','created_at', 'updated_at']
        read_only_fields = ['id','user', 'created_at', 'updated_at']

class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'alert', 'triggered_price', 'message', 'notified_at', 'updated_at']
        read_only_fields = ['id', 'notified_at', 'updated_at']

