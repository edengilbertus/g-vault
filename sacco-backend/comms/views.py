from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from comms.models import MobileMoneyWebhookEvent
from comms.serializers import MobileMoneyWebhookEventSerializer


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
        event = serializer.save(is_processed=True, processed_at=timezone.now())
        return Response({"status": "accepted", "event_id": event.id}, status=status.HTTP_202_ACCEPTED)
