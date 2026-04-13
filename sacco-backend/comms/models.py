from django.conf import settings
from django.db import models


class MobileMoneyWebhookEvent(models.Model):
    class Provider(models.TextChoices):
        AFRICAS_TALKING = "africas_talking", "Africa's Talking"

    provider = models.CharField(max_length=40, choices=Provider.choices, default=Provider.AFRICAS_TALKING)
    event_type = models.CharField(max_length=80, default="unknown")
    external_id = models.CharField(max_length=120, blank=True)
    payload = models.JSONField()
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"WebhookEvent<{self.provider}:{self.event_type}:{self.external_id or 'n/a'}>"


class SmsNotification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    provider = models.CharField(
        max_length=40,
        choices=MobileMoneyWebhookEvent.Provider.choices,
        default=MobileMoneyWebhookEvent.Provider.AFRICAS_TALKING,
    )
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sms_notifications")
    event_type = models.CharField(max_length=80)
    recipient_phone = models.CharField(max_length=32)
    message = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    transaction = models.ForeignKey(
        "finance.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_notifications",
    )
    loan_application = models.ForeignKey(
        "finance.LoanApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_notifications",
    )
    external_message_id = models.CharField(max_length=120, blank=True)
    provider_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"SmsNotification<{self.id} {self.event_type} {self.status}>"
