from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from finance.models import LoanAccount, LoanApplication, SavingsAccount, Transaction
from members.models import User


class FinanceApiTests(APITestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            email="member@bank.test",
            password="StrongPass123!",
            full_name="Member User",
            phone_number="+254700000010",
        )
        self.member_token = Token.objects.create(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.member_token.key}")

    def test_deposit_updates_balance_and_creates_transaction(self):
        response = self.client.post(
            "/api/finance/deposits/",
            {"amount": "5000.00", "payment_method": "mtn", "phone_number": "+256700123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account = SavingsAccount.objects.get(member=self.member)
        self.assertEqual(str(account.available_balance), "5000.00")
        self.assertEqual(Transaction.objects.filter(account=account, tx_type=Transaction.Type.DEPOSIT).count(), 1)

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

        response = self.client.post(
            f"/api/finance/admin/loans/{application.id}/decision/",
            {"action": "approve", "review_note": "Eligible based on profile."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        application.refresh_from_db()
        self.assertEqual(application.status, LoanApplication.Status.APPROVED)
        self.assertTrue(LoanAccount.objects.filter(application=application).exists())
