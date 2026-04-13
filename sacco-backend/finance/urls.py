from django.urls import path

from finance.views import (
    AdminActivityView,
    AdminLoanDecisionView,
    AdminOverviewView,
    AdminPendingLoanApplicationsView,
    DashboardSummaryView,
    DepositCreateView,
    LoanApplicationCreateView,
    MyLoanAccountsView,
    MyLoanApplicationsView,
    TransferCreateView,
    TransactionListView,
    WithdrawalCreateView,
)

urlpatterns = [
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("deposits/", DepositCreateView.as_view(), name="deposit-create"),
    path("transfers/", TransferCreateView.as_view(), name="transfer-create"),
    path("withdrawals/", WithdrawalCreateView.as_view(), name="withdrawal-create"),
    path("loans/applications/", LoanApplicationCreateView.as_view(), name="loan-application-create"),
    path("loans/applications/me/", MyLoanApplicationsView.as_view(), name="loan-application-me"),
    path("loans/accounts/me/", MyLoanAccountsView.as_view(), name="loan-account-me"),
    path("admin/overview/", AdminOverviewView.as_view(), name="admin-overview"),
    path("admin/activity/", AdminActivityView.as_view(), name="admin-activity"),
    path("admin/loans/pending/", AdminPendingLoanApplicationsView.as_view(), name="admin-pending-loans"),
    path("admin/loans/<int:application_id>/decision/", AdminLoanDecisionView.as_view(), name="admin-loan-decision"),
]
