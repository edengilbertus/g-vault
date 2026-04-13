from django.contrib import admin

from finance.models import LoanAccount, LoanApplication, SavingsAccount, Transaction


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ("member", "available_balance", "updated_at")
    search_fields = ("member__email", "member__full_name", "member__phone_number")


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "amount", "purpose", "term_months", "status", "created_at")
    search_fields = ("member__email", "member__full_name", "purpose")
    list_filter = ("status", "term_months", "created_at")


@admin.register(LoanAccount)
class LoanAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "principal", "outstanding_balance", "status", "next_repayment_date")
    search_fields = ("member__email", "member__full_name")
    list_filter = ("status",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "account", "tx_type", "direction", "amount", "status", "created_at")
    search_fields = ("reference", "account__member__email", "description")
    list_filter = ("tx_type", "direction", "status", "created_at")
