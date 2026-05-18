from celery import shared_task
from .models import PriceAlert, NotificationLog
import requests

API_DOMAIN = "http://web:8000"
API_URL = f"{API_DOMAIN}/api/flights/price/"

@shared_task
def check_prices():
    active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE)
    # if not active_alerts:
    #     return JsonResponse({'message': 'No active alerts found.'}, status=status.HTTP_404_NOT_FOUND)
    
    routes = active_alerts.values_list('origin', 'destination').distinct()
    for origin, destination in routes:
        route = f"{origin}-{destination}"
        
        try:
            response = requests.get(
                API_URL, 
                params={'route': route}, 
                timeout=5
            )
            if response.status_code != 200:
                continue
            current_price = response.json().get('price')
        except requests.exceptions.RequestException as e:
            # print(e)
            continue
        route_alerts = active_alerts.filter(origin=origin, destination=destination)
        for alert in route_alerts:
            if current_price <= float(alert.threshold_price):
                send_notification.delay(str(alert.id), current_price)


@shared_task
def send_notification(alert_id, triggered_price):
    alert = PriceAlert.objects.get(id=alert_id)
    message = (
        f"Price alert triggered for {alert.origin}-{alert.destination} "
        f"is now ₹{triggered_price} - below your threshold of  "
        f"₹{alert.threshold_price}."
    )
    NotificationLog.objects.create(
        alert=alert,
        triggered_price=triggered_price,
        message=message
    )
    alert.status = PriceAlert.Status.TRIGGERED
    alert.save()