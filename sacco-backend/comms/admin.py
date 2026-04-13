from django.contrib import admin

from comms.models import MobileMoneyWebhookEvent


@admin.register(MobileMoneyWebhookEvent)
class MobileMoneyWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_type", "external_id", "is_processed", "created_at")
    search_fields = ("external_id", "event_type")
    list_filter = ("provider", "is_processed", "created_at")
