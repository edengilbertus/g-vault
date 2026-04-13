from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from comms.models import MobileMoneyWebhookEvent, SmsNotification
from finance.models import SavingsAccount, Transaction
from members.models import User


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

    def test_mobile_money_success_webhook_completes_pending_deposit(self):
        member = User.objects.create_user(
            email="webhook.member@test.local",
            password="StrongPass123!",
            full_name="Webhook Member",
            phone_number="+256700555000",
        )
        account, _ = SavingsAccount.objects.get_or_create(member=member)
        account.available_balance = "0.00"
        account.save(update_fields=["available_balance", "updated_at"])
        tx = Transaction.objects.create(
            account=account,
            tx_type=Transaction.Type.DEPOSIT,
            direction=Transaction.Direction.CREDIT,
            amount="5000.00",
            status=Transaction.Status.PENDING,
            description="Deposit request via MTN (Pending confirmation)",
            external_reference=member.phone_number,
        )

        payload = {
            "eventType": "payment.success",
            "transactionId": tx.reference,
            "amount": "5000.00",
            "phoneNumber": member.phone_number,
        }

        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value={
                "SMSMessageData": {
                    "Recipients": [
                        {
                            "number": member.phone_number,
                            "status": "Success",
                            "statusCode": 101,
                            "messageId": "AT-WEBHOOK-1",
                        }
                    ]
                }
            },
        ):
            response = self.client.post("/api/comms/webhooks/mobile-money/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        tx.refresh_from_db()
        account.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.COMPLETED)
        self.assertEqual(str(account.available_balance), "5000.00")
        self.assertTrue(
            SmsNotification.objects.filter(
                member=member,
                event_type="deposit.completed",
                status=SmsNotification.Status.SENT,
                transaction=tx,
            ).exists()
        )
