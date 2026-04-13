from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from comms.models import MobileMoneyWebhookEvent
from comms.services import format_ugx, send_member_event_sms
from comms.serializers import MobileMoneyWebhookEventSerializer
from finance.models import Transaction


class MobileMoneyWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = {
            "provider": MobileMoneyWebhookEvent.Provider.AFRICAS_TALKING,
            "event_type": request.data.get("eventType", "unknown"),
            "external_id": request.data.get("transactionId", ""),
            "payload": request.data,
        }
        serializer = MobileMoneyWebhookEventSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(is_processed=False)

        event_type = str(event.event_type).lower()
        transaction_ref = event.external_id

        tx = None
        if transaction_ref:
            tx = (
                Transaction.objects.select_related("account__member")
                .filter(
                    reference=transaction_ref,
                    tx_type=Transaction.Type.DEPOSIT,
                )
                .first()
            )

        if tx and tx.status == Transaction.Status.PENDING:
            if event_type in {"payment.success", "deposit.success", "charge.success", "checkout.success"}:
                with transaction.atomic():
                    account = tx.account
                    account.available_balance += tx.amount
                    account.save(update_fields=["available_balance", "updated_at"])

                    tx.status = Transaction.Status.COMPLETED
                    tx.description = tx.description.replace("(Pending confirmation)", "(Completed)")
                    tx.save(update_fields=["status", "description"])

                send_member_event_sms(
                    member=tx.account.member,
                    event_type="deposit.completed",
                    message=(
                        f"G Vault: Deposit of {format_ugx(tx.amount)} confirmed. "
                        f"Ref: {tx.reference}. New balance: {format_ugx(tx.account.available_balance)}."
                    ),
                    transaction_obj=tx,
                )
            elif event_type in {"payment.failed", "deposit.failed", "charge.failed", "checkout.failed"}:
                tx.status = Transaction.Status.FAILED
                tx.description = tx.description.replace("(Pending confirmation)", "(Failed)")
                tx.save(update_fields=["status", "description"])
                send_member_event_sms(
                    member=tx.account.member,
                    event_type="deposit.failed",
                    message=(
                        f"G Vault: Deposit request for {format_ugx(tx.amount)} failed. "
                        f"Ref: {tx.reference}. No funds were added."
                    ),
                    transaction_obj=tx,
                )

        event.is_processed = True
        event.processed_at = timezone.now()
        event.save(update_fields=["is_processed", "processed_at"])
        return Response({"status": "accepted", "event_id": event.id}, status=status.HTTP_202_ACCEPTED)
