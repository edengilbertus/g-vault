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
