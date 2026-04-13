from rest_framework import status
from rest_framework.test import APITestCase

from comms.models import MobileMoneyWebhookEvent


class CommsApiTests(APITestCase):
    def test_mobile_money_webhook_is_recorded(self):
        payload = {
            "eventType": "payment.success",
            "transactionId": "AT-12345",
            "amount": "5000.00",
            "phoneNumber": "+254700000000",
        }
        response = self.client.post("/api/comms/webhooks/mobile-money/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(MobileMoneyWebhookEvent.objects.filter(external_id="AT-12345").exists())
