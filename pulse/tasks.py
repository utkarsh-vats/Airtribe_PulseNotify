from celery import shared_task
from .models import PriceAlert, NotificationLog
import requests
import logging

logger = logging.getLogger(__name__)

API_DOMAIN = "http://web:8000"
API_URL = f"{API_DOMAIN}/api/flights/price/"

@shared_task
def check_prices():
    active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE)
    if not active_alerts:
        logger.warning("No active alerts found.")
        return
    
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
            logger.error(f"Error fetching price for route {route}: {e}")
            continue
        route_alerts = active_alerts.filter(origin=origin, destination=destination)
        for alert in route_alerts:
            logger.info(f"Checking price for {alert.origin}-{alert.destination}: ₹{current_price}")
            if current_price <= float(alert.threshold_price):
                send_notification.delay(str(alert.id), current_price)


@shared_task
def send_notification(alert_id, triggered_price):
    try:
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
        logger.info(f"Notification sent for {alert.origin}-{alert.destination} with alertID {alert_id}: {message}")
        alert.status = PriceAlert.Status.TRIGGERED
        alert.save()
    except PriceAlert.DoesNotExist:
        logger.warning(f"Alert with ID {alert_id} does not exist - may have been deleted.")