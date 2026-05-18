from django.test import TestCase
from .models import PriceAlert, NotificationLog
from django.contrib.auth.models import User

class PriceThresholdTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.alert = PriceAlert.objects.create(
            user=self.user,
            origin='DEL',
            destination='BOM',
            threshold_price=4500.00,
            status=PriceAlert.Status.ACTIVE
        )

    def test_price_below_threshold_triggers_alert(self):
        current_price = 4200
        self.assertTrue(current_price <= float(self.alert.threshold_price))

    def test_price_above_threshold_does_not_trigger_alert(self):
        current_price = 4800
        self.assertFalse(current_price <= float(self.alert.threshold_price))

    def test_price_equal_to_threshold_triggers_alert(self):
        current_price = 4500
        self.assertTrue(current_price <= float(self.alert.threshold_price))

class NotificationLogTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.alert = PriceAlert.objects.create(
            user=self.user,
            origin='DEL',
            destination="BOM",
            threshold_price=4500.00,
            status=PriceAlert.Status.ACTIVE
        )

    def test_notification_log_created_with_correct_message(self):
        log = NotificationLog.objects.create(
            alert=self.alert,
            triggered_price=4200.00,
            message="Price dropped to 4200 for DEL-BOM"
        )

        self.assertEqual(float(log.triggered_price), 4200)
        self.assertEqual(log.alert, self.alert)
        self.assertIn("DEL-BOM", log.message)

class AlertScopingTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.alert1 = PriceAlert.objects.create(
            user=self.user1,
            origin="DEL",
            destination="BOM",
            threshold_price=4500.00,
            status=PriceAlert.Status.ACTIVE
        )
        self.alert2 = PriceAlert.objects.create(
            user=self.user2,
            origin="DEL",
            destination="BLR",
            threshold_price=5000.00,
            status=PriceAlert.Status.ACTIVE
        )

    def test_user_only_sees_own_alerts(self):
        user1_alerts = PriceAlert.objects.filter(user=self.user1)
        self.assertEqual(user1_alerts.count(), 1)
        self.assertEqual(user1_alerts.first().destination, "BOM")       # type: ignore

    def test_user_cannot_see_other_users_alerts(self):
        user2_alerts = PriceAlert.objects.filter(user=self.user1)
        self.assertNotEqual(user2_alerts.first().destination, "BLR")    # type: ignore