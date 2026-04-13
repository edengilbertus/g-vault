from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from finance.models import LoanAccount, LoanApplication, SavingsAccount, Transaction
from finance.serializers import (
    DepositSerializer,
    LoanAccountSerializer,
    LoanApplicationCreateSerializer,
    LoanApplicationSerializer,
    LoanDecisionSerializer,
    TransactionSerializer,
)

CURRENCY_CODE = "UGX"


class DashboardSummaryView(APIView):
    def get(self, request):
        account, _ = SavingsAccount.objects.get_or_create(member=request.user)
        active_loan = (
            LoanAccount.objects.filter(member=request.user, status=LoanAccount.Status.ACTIVE)
            .order_by("-created_at")
            .first()
        )

        recent_transactions = TransactionSerializer(account.transactions.all()[:5], many=True).data
        payload = {
            "currency_code": CURRENCY_CODE,
            "savings_balance": account.available_balance,
            "active_loan_balance": active_loan.outstanding_balance if active_loan else Decimal("0.00"),
            "next_repayment_date": active_loan.next_repayment_date if active_loan else None,
            "total_shares": account.available_balance,
            "recent_transactions": recent_transactions,
        }
        return Response(payload, status=status.HTTP_200_OK)


class TransactionListView(ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        account, _ = SavingsAccount.objects.get_or_create(member=self.request.user)
        queryset = account.transactions.all()
        limit = self.request.query_params.get("limit")
        if limit and limit.isdigit():
            return queryset[: int(limit)]
        return queryset


class DepositCreateView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = SavingsAccount.objects.get_or_create(member=request.user)
        amount = serializer.validated_data["amount"]
        payment_method = serializer.validated_data["payment_method"]
        phone_number = serializer.validated_data.get("phone_number", "")

        account.available_balance += amount
        account.save(update_fields=["available_balance", "updated_at"])

        tx = Transaction.objects.create(
            account=account,
            tx_type=Transaction.Type.DEPOSIT,
            direction=Transaction.Direction.CREDIT,
            amount=amount,
            status=Transaction.Status.COMPLETED,
            description=f"Deposit via {payment_method.upper()}",
            external_reference=phone_number,
        )

        return Response(
            {
                "currency_code": CURRENCY_CODE,
                "transaction": TransactionSerializer(tx).data,
                "new_balance": account.available_balance,
            },
            status=status.HTTP_201_CREATED,
        )


class LoanApplicationCreateView(CreateAPIView):
    serializer_class = LoanApplicationCreateSerializer


class MyLoanApplicationsView(ListAPIView):
    serializer_class = LoanApplicationSerializer

    def get_queryset(self):
        return LoanApplication.objects.filter(member=self.request.user).order_by("-created_at")


class MyLoanAccountsView(ListAPIView):
    serializer_class = LoanAccountSerializer

    def get_queryset(self):
        return LoanAccount.objects.filter(member=self.request.user).order_by("-created_at")


class AdminOverviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_members = request.user.__class__.objects.count()
        active_loans = LoanAccount.objects.filter(status=LoanAccount.Status.ACTIVE).count()
        total_deposits = SavingsAccount.objects.aggregate(total=Sum("available_balance"))["total"] or Decimal("0.00")
        loan_book = LoanAccount.objects.aggregate(total=Sum("outstanding_balance"))["total"] or Decimal("0.00")
        pending_queue = LoanApplication.objects.filter(status=LoanApplication.Status.PENDING).count()

        return Response(
            {
                "currency_code": CURRENCY_CODE,
                "total_members": total_members,
                "active_loans": active_loans,
                "total_deposits": total_deposits,
                "loan_book": loan_book,
                "np_ratio": Decimal("0.00"),
                "case_queue": pending_queue,
            },
            status=status.HTTP_200_OK,
        )


class AdminPendingLoanApplicationsView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = LoanApplicationSerializer

    def get_queryset(self):
        return LoanApplication.objects.filter(status=LoanApplication.Status.PENDING).order_by("created_at")


class AdminLoanDecisionView(APIView):
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request, application_id):
        application = get_object_or_404(LoanApplication, pk=application_id)
        serializer = LoanDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if application.status != LoanApplication.Status.PENDING:
            return Response(
                {"detail": "Only pending applications can be actioned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = serializer.validated_data["action"]
        note = serializer.validated_data.get("review_note", "")
        application.review_note = note
        application.reviewer = request.user
        application.reviewed_at = timezone.now()

        if action == "approve":
            application.status = LoanApplication.Status.APPROVED
            application.save(update_fields=["status", "review_note", "reviewer", "reviewed_at", "updated_at"])

            total_repayable = (application.amount * Decimal("1.18")).quantize(Decimal("0.01"))
            loan = LoanAccount.objects.create(
                application=application,
                member=application.member,
                principal=application.amount,
                term_months=application.term_months,
                outstanding_balance=total_repayable,
                next_repayment_date=timezone.now().date() + timedelta(days=30),
            )

            account, _ = SavingsAccount.objects.get_or_create(member=application.member)
            account.available_balance += application.amount
            account.save(update_fields=["available_balance", "updated_at"])

            Transaction.objects.create(
                account=account,
                loan=loan,
                tx_type=Transaction.Type.LOAN_DISBURSEMENT,
                direction=Transaction.Direction.CREDIT,
                amount=application.amount,
                status=Transaction.Status.COMPLETED,
                description=f"Loan disbursement for application #{application.id}",
            )
        else:
            application.status = LoanApplication.Status.REJECTED
            application.save(update_fields=["status", "review_note", "reviewer", "reviewed_at", "updated_at"])

        return Response(LoanApplicationSerializer(application).data, status=status.HTTP_200_OK)
