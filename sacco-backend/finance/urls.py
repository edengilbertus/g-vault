from django.urls import path

from finance.views import (
    AdminLoanDecisionView,
    AdminOverviewView,
    AdminPendingLoanApplicationsView,
    DashboardSummaryView,
    DepositCreateView,
    LoanApplicationCreateView,
    MyLoanAccountsView,
    MyLoanApplicationsView,
    TransactionListView,
)

urlpatterns = [
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("deposits/", DepositCreateView.as_view(), name="deposit-create"),
    path("loans/applications/", LoanApplicationCreateView.as_view(), name="loan-application-create"),
    path("loans/applications/me/", MyLoanApplicationsView.as_view(), name="loan-application-me"),
    path("loans/accounts/me/", MyLoanAccountsView.as_view(), name="loan-account-me"),
    path("admin/overview/", AdminOverviewView.as_view(), name="admin-overview"),
    path("admin/loans/pending/", AdminPendingLoanApplicationsView.as_view(), name="admin-pending-loans"),
    path("admin/loans/<int:application_id>/decision/", AdminLoanDecisionView.as_view(), name="admin-loan-decision"),
]
