from unittest.mock import patch

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from comms.models import SmsNotification
from finance.models import LoanAccount, LoanApplication, SavingsAccount, Transaction
from members.models import User


class FinanceApiTests(APITestCase):
    @staticmethod
    def sms_provider_response(message_id: str) -> dict:
        return {
            "SMSMessageData": {
                "Recipients": [
                    {
                        "number": "+256700000000",
                        "status": "Success",
                        "statusCode": 101,
                        "messageId": message_id,
                    }
                ]
            }
        }

    def setUp(self):
        self.member = User.objects.create_user(
            email="member@bank.test",
            password="StrongPass123!",
            full_name="Member User",
            phone_number="+254700000010",
        )
        self.member_token = Token.objects.create(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.member_token.key}")

    def test_mobile_money_deposit_stays_pending_until_confirmation(self):
        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value=self.sms_provider_response("AT-DEPOSIT-1"),
        ):
            response = self.client.post(
                "/api/finance/deposits/",
                {"amount": "5000.00", "payment_method": "mtn", "phone_number": "+256700123456"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account = SavingsAccount.objects.get(member=self.member)
        self.assertEqual(str(account.available_balance), "0.00")
        tx = Transaction.objects.get(account=account, tx_type=Transaction.Type.DEPOSIT)
        self.assertEqual(tx.status, Transaction.Status.PENDING)
        self.assertTrue(
            SmsNotification.objects.filter(
                member=self.member, event_type="deposit.initiated", status=SmsNotification.Status.SENT
            ).exists()
        )

    def test_card_deposit_completes_immediately(self):
        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value=self.sms_provider_response("AT-DEPOSIT-2"),
        ):
            response = self.client.post(
                "/api/finance/deposits/",
                {"amount": "5000.00", "payment_method": "card"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account = SavingsAccount.objects.get(member=self.member)
        self.assertEqual(str(account.available_balance), "5000.00")
        tx = Transaction.objects.get(account=account, tx_type=Transaction.Type.DEPOSIT)
        self.assertEqual(tx.status, Transaction.Status.COMPLETED)
        self.assertTrue(
            SmsNotification.objects.filter(
                member=self.member, event_type="deposit.completed", status=SmsNotification.Status.SENT
            ).exists()
        )

    def test_member_can_submit_loan_application(self):
        payload = {
            "amount": "25000.00",
            "purpose": "business",
            "term_months": 24,
            "collateral_type": "vehicle",
            "collateral_value": "30000.00",
            "applicant_first_name": "Member",
            "applicant_last_name": "User",
            "applicant_id_number": "ID-001",
        }
        response = self.client.post("/api/finance/loans/applications/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoanApplication.objects.filter(member=self.member).count(), 1)

    def test_member_can_create_transfer(self):
        account = SavingsAccount.objects.get(member=self.member)
        account.available_balance = "10000.00"
        account.save(update_fields=["available_balance", "updated_at"])

        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value=self.sms_provider_response("AT-TRANSFER-1"),
        ):
            response = self.client.post(
                "/api/finance/transfers/",
                {
                    "transfer_type": "external",
                    "destination": "member-abc@example.com",
                    "amount": "1000.00",
                    "note": "School fees",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account.refresh_from_db()
        self.assertEqual(str(account.available_balance), "9000.00")
        self.assertTrue(
            SmsNotification.objects.filter(
                member=self.member, event_type="transfer.completed", status=SmsNotification.Status.SENT
            ).exists()
        )

    def test_member_can_create_mobile_withdrawal(self):
        account = SavingsAccount.objects.get(member=self.member)
        account.available_balance = "15000.00"
        account.save(update_fields=["available_balance", "updated_at"])

        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value=self.sms_provider_response("AT-WITHDRAWAL-1"),
        ):
            response = self.client.post(
                "/api/finance/withdrawals/",
                {
                    "destination_type": "mobile",
                    "amount": "2500.00",
                    "mobile_network": "mtn",
                    "phone_number": "+256700222333",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account.refresh_from_db()
        self.assertEqual(str(account.available_balance), "12500.00")
        self.assertTrue(
            SmsNotification.objects.filter(
                member=self.member, event_type="withdrawal.completed", status=SmsNotification.Status.SENT
            ).exists()
        )

    def test_admin_can_approve_loan_application(self):
        application = LoanApplication.objects.create(
            member=self.member,
            amount="10000.00",
            purpose="personal",
            term_months=12,
        )

        admin_user = User.objects.create_superuser(
            email="admin@bank.test",
            password="StrongPass123!",
            full_name="Admin User",
            phone_number="+254700000011",
        )
        admin_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token.key}")

        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value=self.sms_provider_response("AT-LOAN-APPROVE-1"),
        ):
            response = self.client.post(
                f"/api/finance/admin/loans/{application.id}/decision/",
                {"action": "approve", "review_note": "Eligible based on profile."},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, LoanApplication.Status.APPROVED)
        self.assertTrue(LoanAccount.objects.filter(application=application).exists())
        self.assertTrue(
            SmsNotification.objects.filter(
                member=self.member, event_type="loan.approved", status=SmsNotification.Status.SENT
            ).exists()
        )

    def test_admin_can_reject_loan_application(self):
        application = LoanApplication.objects.create(
            member=self.member,
            amount="9000.00",
            purpose="education",
            term_months=12,
        )

        admin_user = User.objects.create_superuser(
            email="admin2@bank.test",
            password="StrongPass123!",
            full_name="Admin User Two",
            phone_number="+254700000012",
        )
        admin_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token.key}")

        with patch(
            "comms.services.send_sms_via_africas_talking",
            return_value=self.sms_provider_response("AT-LOAN-REJECT-1"),
        ):
            response = self.client.post(
                f"/api/finance/admin/loans/{application.id}/decision/",
                {"action": "reject", "review_note": "Insufficient repayment capacity."},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, LoanApplication.Status.REJECTED)
        self.assertTrue(
            SmsNotification.objects.filter(
                member=self.member, event_type="loan.rejected", status=SmsNotification.Status.SENT
            ).exists()
        )

    def test_admin_overview_includes_operational_metrics(self):
        admin_user = User.objects.create_superuser(
            email="admin3@bank.test",
            password="StrongPass123!",
            full_name="Admin User Three",
            phone_number="+254700000013",
        )
        admin_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token.key}")

        response = self.client.get("/api/finance/admin/overview/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_transactions", response.data)
        self.assertIn("total_notifications", response.data)
        self.assertIn("failed_notifications", response.data)

    def test_admin_activity_feed_returns_live_events(self):
        account = SavingsAccount.objects.get(member=self.member)
        Transaction.objects.create(
            account=account,
            tx_type=Transaction.Type.DEPOSIT,
            direction=Transaction.Direction.CREDIT,
            amount="1000.00",
            status=Transaction.Status.COMPLETED,
            description="Test deposit",
        )
        LoanApplication.objects.create(
            member=self.member,
            amount="5000.00",
            purpose="business",
            term_months=12,
        )

        admin_user = User.objects.create_superuser(
            email="admin4@bank.test",
            password="StrongPass123!",
            full_name="Admin User Four",
            phone_number="+254700000014",
        )
        admin_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token.key}")

        response = self.client.get("/api/finance/admin/activity/?limit=10")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)
        event_types = {item["event_type"] for item in response.data}
        self.assertIn("transaction.deposit", event_types)
        self.assertIn("loan.submitted", event_types)
