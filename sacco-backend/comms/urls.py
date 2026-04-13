from django.urls import path

from comms.views import MobileMoneyWebhookView

urlpatterns = [
    path("webhooks/mobile-money/", MobileMoneyWebhookView.as_view(), name="mobile-money-webhook"),
]
