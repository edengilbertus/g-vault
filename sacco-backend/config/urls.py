from django.contrib import admin
from django.urls import include, path

from config.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health"),
    path("api/auth/", include("members.urls")),
    path("api/finance/", include("finance.urls")),
    path("api/comms/", include("comms.urls")),
    path("api/reports/", include("reports.urls")),
]
