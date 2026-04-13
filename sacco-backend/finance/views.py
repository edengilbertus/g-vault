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

from comms.models import SmsNotification
from comms.services import format_ugx, send_member_event_sms
from finance.models import LoanAccount, LoanApplication, SavingsAccount, Transaction
from finance.serializers import (
    DepositSerializer,
    LoanAccountSerializer,
    LoanApplicationCreateSerializer,
    LoanApplicationSerializer,
    LoanDecisionSerializer,
    TransactionSerializer,
    TransferSerializer,
    WithdrawalSerializer,
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
        phone_number = serializer.validated_data.get("phone_number", "").strip()
        is_mobile_money = payment_method in {"mtn", "airtel"}

        tx_status = Transaction.Status.PENDING if is_mobile_money else Transaction.Status.COMPLETED
        tx_description = (
            f"Deposit request via {payment_method.upper()} (Pending confirmation)"
            if is_mobile_money
            else f"Deposit via {payment_method.upper()}"
        )

        if not is_mobile_money:
            account.available_balance += amount
            account.save(update_fields=["available_balance", "updated_at"])

        tx = Transaction.objects.create(
            account=account,
            tx_type=Transaction.Type.DEPOSIT,
            direction=Transaction.Direction.CREDIT,
            amount=amount,
            status=tx_status,
            description=tx_description,
            external_reference=phone_number,
        )

        if is_mobile_money:
            send_member_event_sms(
                member=request.user,
                event_type="deposit.initiated",
                message=(
                    f"G Vault: Deposit request of {format_ugx(amount)} initiated via {payment_method.upper()}. "
                    f"Ref: {tx.reference}. Approve on your phone to complete."
                ),
                transaction_obj=tx,
            )
        else:
            send_member_event_sms(
                member=request.user,
                event_type="deposit.completed",
                message=(
                    f"G Vault: Deposit of {format_ugx(amount)} received. "
                    f"Ref: {tx.reference}. New balance: {format_ugx(account.available_balance)}."
                ),
                transaction_obj=tx,
            )

        return Response(
            {
                "currency_code": CURRENCY_CODE,
                "transaction": TransactionSerializer(tx).data,
                "new_balance": account.available_balance,
            },
            status=status.HTTP_201_CREATED,
        )


class TransferCreateView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = SavingsAccount.objects.get_or_create(member=request.user)
        amount = serializer.validated_data["amount"]

        if account.available_balance < amount:
            return Response({"detail": "Insufficient balance for transfer."}, status=status.HTTP_400_BAD_REQUEST)

        account.available_balance -= amount
        account.save(update_fields=["available_balance", "updated_at"])

        destination = serializer.validated_data["destination"]
        note = serializer.validated_data.get("note", "")
        transfer_type = serializer.validated_data["transfer_type"]

        tx = Transaction.objects.create(
            account=account,
            tx_type=Transaction.Type.TRANSFER,
            direction=Transaction.Direction.DEBIT,
            amount=amount,
            status=Transaction.Status.COMPLETED,
            description=f"{transfer_type.capitalize()} transfer: {note or destination}",
            external_reference=destination,
        )
        send_member_event_sms(
            member=request.user,
            event_type="transfer.completed",
            message=(
                f"G Vault: Transfer of {format_ugx(amount)} to {destination} completed. "
                f"Ref: {tx.reference}. New balance: {format_ugx(account.available_balance)}."
            ),
            transaction_obj=tx,
        )

        return Response(
            {
                "currency_code": CURRENCY_CODE,
                "transaction": TransactionSerializer(tx).data,
                "new_balance": account.available_balance,
            },
            status=status.HTTP_201_CREATED,
        )


class WithdrawalCreateView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account, _ = SavingsAccount.objects.get_or_create(member=request.user)
        amount = serializer.validated_data["amount"]

        if account.available_balance < amount:
            return Response({"detail": "Insufficient balance for withdrawal."}, status=status.HTTP_400_BAD_REQUEST)

        account.available_balance -= amount
        account.save(update_fields=["available_balance", "updated_at"])

        destination_type = serializer.validated_data["destination_type"]
        if destination_type == "bank":
            destination_descriptor = serializer.validated_data["bank_name"]
        else:
            destination_descriptor = serializer.validated_data["phone_number"]

        tx = Transaction.objects.create(
            account=account,
            tx_type=Transaction.Type.WITHDRAWAL,
            direction=Transaction.Direction.DEBIT,
            amount=amount,
            status=Transaction.Status.COMPLETED,
            description=f"Withdrawal to {destination_type}: {destination_descriptor}",
            external_reference=destination_descriptor,
        )
        send_member_event_sms(
            member=request.user,
            event_type="withdrawal.completed",
            message=(
                f"G Vault: Withdrawal of {format_ugx(amount)} to {destination_descriptor} completed. "
                f"Ref: {tx.reference}. New balance: {format_ugx(account.available_balance)}."
            ),
            transaction_obj=tx,
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
        total_transactions = Transaction.objects.count()
        total_notifications = SmsNotification.objects.count()
        failed_notifications = SmsNotification.objects.filter(status=SmsNotification.Status.FAILED).count()

        return Response(
            {
                "currency_code": CURRENCY_CODE,
                "total_members": total_members,
                "active_loans": active_loans,
                "total_deposits": total_deposits,
                "loan_book": loan_book,
                "np_ratio": Decimal("0.00"),
                "case_queue": pending_queue,
                "total_transactions": total_transactions,
                "total_notifications": total_notifications,
                "failed_notifications": failed_notifications,
            },
            status=status.HTTP_200_OK,
        )


class AdminActivityView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        limit_param = request.query_params.get("limit", "12")
        limit = 12
        if isinstance(limit_param, str) and limit_param.isdigit():
            limit = int(limit_param)
        limit = max(1, min(limit, 100))

        events = []

        users = request.user.__class__.objects.order_by("-date_joined")[:limit]
        for user in users:
            role = "Admin" if user.is_staff else "Member"
            events.append(
                {
                    "id": f"user-{user.id}",
                    "occurred_at": user.date_joined,
                    "event_type": "user.joined",
                    "message": f"{role} account created.",
                    "actor": user.email,
                    "severity": "info",
                }
            )

        transactions = Transaction.objects.select_related("account__member").order_by("-created_at")[:limit]
        for tx in transactions:
            tx_name = tx.tx_type.replace("_", " ")
            events.append(
                {
                    "id": f"tx-{tx.id}",
                    "occurred_at": tx.created_at,
                    "event_type": f"transaction.{tx.tx_type}",
                    "message": f"{tx_name.capitalize()} of {format_ugx(tx.amount)}. Ref: {tx.reference}.",
                    "actor": tx.account.member.email,
                    "severity": "action",
                }
            )

        loan_submissions = LoanApplication.objects.select_related("member").order_by("-created_at")[:limit]
        for application in loan_submissions:
            events.append(
                {
                    "id": f"loan-submitted-{application.id}",
                    "occurred_at": application.created_at,
                    "event_type": "loan.submitted",
                    "message": (
                        f"Loan application #{application.id} submitted for {format_ugx(application.amount)}."
                    ),
                    "actor": application.member.email,
                    "severity": "action",
                }
            )

        loan_reviews = (
            LoanApplication.objects.select_related("member", "reviewer")
            .filter(reviewed_at__isnull=False)
            .order_by("-reviewed_at")[:limit]
        )
        for application in loan_reviews:
            events.append(
                {
                    "id": f"loan-reviewed-{application.id}",
                    "occurred_at": application.reviewed_at,
                    "event_type": f"loan.{application.status}",
                    "message": (
                        f"Loan application #{application.id} {application.status} for "
                        f"{format_ugx(application.amount)}."
                    ),
                    "actor": application.reviewer.email if application.reviewer else "system",
                    "severity": "action",
                }
            )

        notifications = SmsNotification.objects.select_related("member").order_by("-created_at")[:limit]
        for notification in notifications:
            events.append(
                {
                    "id": f"sms-{notification.id}",
                    "occurred_at": notification.created_at,
                    "event_type": f"sms.{notification.status}",
                    "message": (
                        f"SMS {notification.status} for {notification.event_type} "
                        f"to {notification.recipient_phone}."
                    ),
                    "actor": notification.member.email,
                    "severity": "system",
                }
            )

        sorted_events = sorted(events, key=lambda item: item["occurred_at"], reverse=True)[:limit]
        return Response(sorted_events, status=status.HTTP_200_OK)


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

            disbursement_tx = Transaction.objects.create(
                account=account,
                loan=loan,
                tx_type=Transaction.Type.LOAN_DISBURSEMENT,
                direction=Transaction.Direction.CREDIT,
                amount=application.amount,
                status=Transaction.Status.COMPLETED,
                description=f"Loan disbursement for application #{application.id}",
            )
            send_member_event_sms(
                member=application.member,
                event_type="loan.approved",
                message=(
                    f"G Vault: Loan application #{application.id} approved and disbursed for "
                    f"{format_ugx(application.amount)}. Ref: {disbursement_tx.reference}."
                ),
                transaction_obj=disbursement_tx,
                loan_application=application,
            )
        else:
            application.status = LoanApplication.Status.REJECTED
            application.save(update_fields=["status", "review_note", "reviewer", "reviewed_at", "updated_at"])
            send_member_event_sms(
                member=application.member,
                event_type="loan.rejected",
                message=(
                    f"G Vault: Loan application #{application.id} for {format_ugx(application.amount)} "
                    f"was rejected. Ref: APP-{application.id}."
                ),
                loan_application=application,
            )

        return Response(LoanApplicationSerializer(application).data, status=status.HTTP_200_OK)
