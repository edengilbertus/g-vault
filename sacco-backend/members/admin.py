from django.contrib import admin

from members.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "phone_number", "is_staff", "is_active", "date_joined")
    search_fields = ("email", "full_name", "phone_number", "national_id")
    list_filter = ("is_staff", "is_active", "date_joined")
    ordering = ("-date_joined",)
