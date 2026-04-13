from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.db import models


def generate_tx_reference() -> str:
    return f"TXN-{uuid4().hex[:12].upper()}"


class SavingsAccount(models.Model):
    member = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="savings_account")
    available_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SavingsAccount<{self.member.email}>"


class LoanApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        DISBURSED = "disbursed", "Disbursed"

    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loan_applications")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    purpose = models.CharField(max_length=120)
    term_months = models.PositiveIntegerField()
    collateral_type = models.CharField(max_length=120, blank=True)
    collateral_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    applicant_first_name = models.CharField(max_length=120, blank=True)
    applicant_last_name = models.CharField(max_length=120, blank=True)
    applicant_id_number = models.CharField(max_length=120, blank=True)
    employer = models.CharField(max_length=255, blank=True)
    monthly_salary = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    review_note = models.TextField(blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_loan_applications",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LoanApplication<{self.id} {self.member.email} {self.status}>"


class LoanAccount(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        DEFAULTED = "defaulted", "Defaulted"

    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name="loan_account")
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loan_accounts")
    principal = models.DecimalField(max_digits=14, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("18.00"))
    term_months = models.PositiveIntegerField()
    outstanding_balance = models.DecimalField(max_digits=14, decimal_places=2)
    next_repayment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LoanAccount<{self.id} {self.member.email} {self.status}>"


class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        TRANSFER = "transfer", "Transfer"
        LOAN_DISBURSEMENT = "loan_disbursement", "Loan Disbursement"
        LOAN_REPAYMENT = "loan_repayment", "Loan Repayment"

    class Direction(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    account = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE, related_name="transactions")
    loan = models.ForeignKey(LoanAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    tx_type = models.CharField(max_length=32, choices=Type.choices)
    direction = models.CharField(max_length=16, choices=Direction.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=32, unique=True, default=generate_tx_reference)
    external_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Transaction<{self.reference} {self.tx_type} {self.amount}>"
