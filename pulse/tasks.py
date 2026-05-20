import logging
from celery import shared_task
from .models import PriceAlert, NotificationLog
from .services import PriceService

logger = logging.getLogger(__name__)

price_service = PriceService()

@shared_task
def check_prices():
    active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE)
    if not active_alerts:
        logger.warning("No active alerts found.")
        return
    
    routes = active_alerts.values_list('origin', 'destination').distinct()
    for origin, destination in routes:
        # ************
        # Previously used internal HTTP call — now handled by PriceService with auto-fallback to mock data
        # ************
        try:
            price = price_service.get_price(origin, destination)
            if price is None:
                logger.warning(f"No price found for route {origin}-{destination}")
                continue
            current_price = float(price)
        except Exception as e:
            logger.error(f"Error fetching price for route {origin}-{destination}: {e}")
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