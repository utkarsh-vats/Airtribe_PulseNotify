import uuid
from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserProfile(BaseModel):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USER)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class PriceAlert(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        TRIGGERED = 'triggered', 'Triggered'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    threshold_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self) -> str:
        return f"{self.origin}-{self.destination} @ ₹{self.threshold_price}"
    
class NotificationLog(BaseModel):
    alert = models.ForeignKey(PriceAlert, on_delete=models.CASCADE, related_name='notifications')
    triggered_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    notified_at = models.DateTimeField(auto_now_add=True)



