from django.contrib import admin

from comms.models import MobileMoneyWebhookEvent, SmsNotification


@admin.register(MobileMoneyWebhookEvent)
class MobileMoneyWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_type", "external_id", "is_processed", "created_at")
    search_fields = ("external_id", "event_type")
    list_filter = ("provider", "is_processed", "created_at")


@admin.register(SmsNotification)
class SmsNotificationAdmin(admin.ModelAdmin):
    list_display = ("event_type", "member", "recipient_phone", "status", "external_message_id", "created_at")
    search_fields = ("member__email", "recipient_phone", "event_type", "external_message_id")
    list_filter = ("provider", "status", "event_type", "created_at")
