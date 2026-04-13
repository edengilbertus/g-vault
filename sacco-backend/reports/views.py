from datetime import date
from decimal import Decimal

from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from finance.models import SavingsAccount, Transaction
from finance.serializers import TransactionSerializer

CURRENCY_CODE = "UGX"


class AccountStatementView(APIView):
    def get(self, request):
        account, _ = SavingsAccount.objects.get_or_create(member=request.user)

        start_raw = request.query_params.get("start_date")
        end_raw = request.query_params.get("end_date")
        today = date.today()

        start_date = date.fromisoformat(start_raw) if start_raw else today.replace(day=1)
        end_date = date.fromisoformat(end_raw) if end_raw else today

        transactions = account.transactions.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)

        credits = (
            transactions.filter(direction=Transaction.Direction.CREDIT, status=Transaction.Status.COMPLETED).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )
        debits = (
            transactions.filter(direction=Transaction.Direction.DEBIT, status=Transaction.Status.COMPLETED).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        payload = {
            "currency_code": CURRENCY_CODE,
            "period": {"start_date": start_date, "end_date": end_date},
            "opening_balance": account.available_balance - credits + debits,
            "closing_balance": account.available_balance,
            "total_credits": credits,
            "total_debits": debits,
            "transactions": TransactionSerializer(transactions, many=True).data,
        }
        return Response(payload, status=status.HTTP_200_OK)
