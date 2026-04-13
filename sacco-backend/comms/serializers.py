from rest_framework import serializers

from comms.models import MobileMoneyWebhookEvent


class MobileMoneyWebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileMoneyWebhookEvent
        fields = ("provider", "event_type", "external_id", "payload")
