import logging
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from .models import PriceAlert, NotificationLog
from .services import PriceService
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

price_service = PriceService()

@shared_task(bind=True, soft_time_limit=120, time_limit=130)
def check_prices(self):
    try:
        active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE)
        if not active_alerts:
            logger.warning("No active alerts found.")
            return
        
        expired = active_alerts.filter(
            travel_date__isnull=False,
            travel_date__lt=timezone.now().date()
        )
        expired_count = expired.update(status=PriceAlert.Status.EXPIRED)
        if expired_count:
            logger.info(f"Expired {expired_count} alerts past travel date.")

        active_alerts = active_alerts.filter(status=PriceAlert.Status.ACTIVE)
        
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
                logger.info(f"Checking price for {alert.origin.code}-{alert.destination.code}: ₹{current_price}")
                if current_price <= float(alert.threshold_price):
                    if alert.last_notified_price is None:
                        send_notification.delay(str(alert.id), current_price)
                    else:
                        if alert.last_notified_at:
                            cooldown = timedelta(minutes=alert.notification_cooldown_minutes)
                            if timezone.now() - alert.last_notified_at < cooldown:
                                logger.debug(f"Skipping {alert.origin.code}-{alert.destination.code}: cooldown active")
                                continue
                        if current_price < float(alert.last_notified_price):
                            send_notification.delay(str(alert.id), current_price)
    except SoftTimeLimitExceeded:
        logger.error("check_prices task exceeded time limit of 120s and was forcefully terminated.")
        return


@shared_task(soft_time_limit=30, time_limit=40)
def send_notification(alert_id, triggered_price):
    try:
        alert = PriceAlert.objects.get(id=alert_id)
        message = (
            f"Price alert triggered for {alert.origin.code}-{alert.destination.code} "
            f"is now ₹{triggered_price} - below your threshold of  "
            f"₹{alert.threshold_price}."
        )
        NotificationLog.objects.create(
            alert=alert,
            triggered_price=triggered_price,
            message=message
        )
        logger.info(f"Notification sent for {alert.origin.code}-{alert.destination.code} with alertID {alert_id}: {message}")
        alert.last_notified_at = timezone.now()
        alert.last_notified_price = triggered_price
        alert.save()
    except PriceAlert.DoesNotExist:
        logger.warning(f"Alert with ID {alert_id} does not exist - may have been deleted.")
    except SoftTimeLimitExceeded:
        logger.error(f"send_notification task for alert {alert_id} exceeded time limit!")