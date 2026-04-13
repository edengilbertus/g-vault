from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from finance.models import SavingsAccount, Transaction
from members.models import User


class ReportApiTests(APITestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            email="report-member@bank.test",
            password="StrongPass123!",
            full_name="Report Member",
            phone_number="+254700000020",
        )
        token = Token.objects.create(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.account = SavingsAccount.objects.get(member=self.member)
        Transaction.objects.create(
            account=self.account,
            tx_type=Transaction.Type.DEPOSIT,
            direction=Transaction.Direction.CREDIT,
            amount="1000.00",
            status=Transaction.Status.COMPLETED,
            description="Initial deposit",
        )
        self.account.available_balance = "1000.00"
        self.account.save(update_fields=["available_balance", "updated_at"])

    def test_current_statement_returns_balances(self):
        response = self.client.get("/api/reports/statements/current/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("closing_balance", response.data)
        self.assertIn("transactions", response.data)
