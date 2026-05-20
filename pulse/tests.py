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

class DuplicateUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
    def test_duplicate_user_creation(self):
        response = self.client.post(
            '/api/auth/register/', 
            data = {
                'username': 'testuser',
                'password': 'testpassword',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)

class AdminSummaryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adminTestUser', password='adminTestPassword')
        # response = self.client.login(username='adminTestUser', password='adminTestPassword')

    def test_regular_user_accessing_admin_summary(self):
        loginResponse = self.client.post(
            '/api/auth/login/',
            data = {
                'username': 'adminTestUser',
                'password': 'adminTestPassword'
            },
            format='json'
        )
        accessToken = loginResponse.data['access']      # type: ignore
        response = self.client.get('/api/admin/summary/', HTTP_AUTHORIZATION=f"Bearer {accessToken}")
        self.assertEqual(response.status_code, 403)

class DeactivationAlertTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.alert = PriceAlert.objects.create(
            user=self.user,
            origin='DEL',
            destination='BOM',
            threshold_price=4500.00,
            status=PriceAlert.Status.ACTIVE
        )

    def test_alert_deactivation_status_change_to_INACTIVE(self):
        loginResponse = self.client.post(
            '/api/auth/login/',
            data = {
                'username': 'testuser',
                'password': 'testpassword'
            },
            format='json'
        )
        accessToken = loginResponse.data['access']      # type: ignore 
        response = self.client.delete(f'/api/alerts/{self.alert.id}/', HTTP_AUTHORIZATION=f"Bearer {accessToken}")
        self.alert.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.alert.status, PriceAlert.Status.INACTIVE)

class MockPriceFeedTest(TestCase):
    def test_mock_price_feed_response_for_unknown_route(self):
        response = self.client.get('/api/flights/price/?route=XXX-YYY')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid route.'})





