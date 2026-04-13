from django.urls import path

from reports.views import AccountStatementView

urlpatterns = [
    path("statements/current/", AccountStatementView.as_view(), name="current-statement"),
]
