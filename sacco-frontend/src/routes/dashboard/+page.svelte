<script lang="ts">
	import { goto } from '$app/navigation';
	import DepositModal from '$lib/components/DepositModal.svelte';
	import { fetchDashboardSummary, fetchMyLoanAccounts, type TransactionApi } from '$lib/api/client';
	import { getStoredToken, getStoredUser } from '$lib/auth/session';
	import MemberNav from '$lib/components/MemberNav.svelte';
	import { onDestroy, onMount } from 'svelte';

	let showDepositModal = $state(false);
	let isLoading = $state(true);
	let loadError = $state('');

	let memberName = $state('Member');
	let savingsBalance = $state(0);
	let loanBalance = $state(0);
	let hasNextRepayment = $state(false);
	let nextRepaymentDateLabel = $state('—');
	let estimatedMonthlyRepayment = $state(0);
	let loanProgressPercent = $state(0);
	let loanPaidAmount = $state(0);
	let loanRemainingAmount = $state(0);
	let loanCardNote = $state('No active loan');
	let loanProgressMeta = $state('No active loan to track');
	let pendingDepositCount = $state(0);
	let pendingDepositAmount = $state(0);

	type DashboardTransaction = {
		id: string;
		merchant: string;
		category: string;
		amount: number;
		date: string;
		type: 'credit' | 'debit' | 'transfer';
		status: string;
	};

	let transactions = $state<DashboardTransaction[]>([]);
	let refreshTimer: ReturnType<typeof setTimeout> | null = null;

	function clearRefreshTimer() {
		if (refreshTimer) {
			clearTimeout(refreshTimer);
			refreshTimer = null;
		}
	}

	function formatAmount(n: number): string {
		const abs = Math.round(Math.abs(n)).toLocaleString('en-UG');
		return (n >= 0 ? '+' : '−') + ' UGX ' + abs;
	}

	function formatMoney(n: number): string {
		return `UGX ${Math.round(n).toLocaleString('en-UG')}`;
	}

	function toTransactionView(tx: TransactionApi): DashboardTransaction {
		const createdAt = new Date(tx.created_at);
		const numericAmount = Number(tx.amount);
		const signedAmount = tx.direction === 'debit' ? -numericAmount : numericAmount;
		const normalizedType: DashboardTransaction['type'] =
			tx.tx_type === 'transfer' ? 'transfer' : tx.direction === 'credit' ? 'credit' : 'debit';

		return {
			id: tx.reference,
			merchant: tx.description || tx.tx_type.replaceAll('_', ' ').toUpperCase(),
			category: tx.tx_type.replaceAll('_', ' '),
			amount: signedAmount,
			date: createdAt.toLocaleDateString('en-UG', { month: 'short', day: 'numeric' }),
			type: normalizedType,
			status: tx.status
		};
	}

	function transactionBadgeClass(tx: DashboardTransaction): string {
		if (tx.status === 'failed') return 'badge-error';
		if (tx.status === 'pending') return 'badge-pending';
		if (tx.type === 'credit') return 'badge-success';
		if (tx.type === 'debit') return 'badge-pending';
		return '';
	}

	async function loadDashboard() {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		clearRefreshTimer();
		isLoading = true;
		loadError = '';
		try {
			const [summary, loanAccounts] = await Promise.all([
				fetchDashboardSummary(token),
				fetchMyLoanAccounts(token)
			]);

			savingsBalance = Number(summary.savings_balance);
			pendingDepositCount = Number(summary.pending_deposit_count ?? 0);
			pendingDepositAmount = Number(summary.pending_deposit_amount ?? 0);
			transactions = summary.recent_transactions.map(toTransactionView);
			hasNextRepayment = Boolean(summary.next_repayment_date);
			nextRepaymentDateLabel = summary.next_repayment_date
				? new Date(summary.next_repayment_date).toLocaleDateString('en-UG', {
						month: 'short',
						day: 'numeric',
						year: 'numeric'
					})
				: 'No repayment due';

			const activeLoan = loanAccounts.find((loan) => loan.status === 'active');
			if (activeLoan) {
				loanBalance = Number(activeLoan.outstanding_balance);
				estimatedMonthlyRepayment = Math.round(loanBalance / activeLoan.term_months);
				loanRemainingAmount = loanBalance;
				loanCardNote = `${Number(activeLoan.interest_rate).toFixed(2)}% APR · ${activeLoan.term_months} months`;
				loanProgressMeta = `Disbursed ${new Date(activeLoan.created_at).toLocaleDateString('en-UG', { month: 'short', year: 'numeric' })} · ${activeLoan.term_months}-month term`;

				const totalLoanCost = Number(activeLoan.principal) * 1.18;
				loanPaidAmount = Math.max(totalLoanCost - loanBalance, 0);
				loanProgressPercent = totalLoanCost > 0 ? Math.min(100, (loanPaidAmount / totalLoanCost) * 100) : 0;
			} else {
				loanBalance = 0;
				estimatedMonthlyRepayment = 0;
				loanProgressPercent = 0;
				loanPaidAmount = 0;
				loanRemainingAmount = 0;
				loanCardNote = 'No active loan';
				loanProgressMeta = 'No active loan to track';
			}
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'Unable to load dashboard data.';
		} finally {
			isLoading = false;
			if (transactions.some((tx) => tx.status === 'pending')) {
				refreshTimer = setTimeout(() => {
					void loadDashboard();
				}, 15000);
			}
		}
	}

	onMount(() => {
		const user = getStoredUser();
		if (user) {
			memberName = user.full_name;
		}
		void loadDashboard();
	});

	onDestroy(() => {
		clearRefreshTimer();
	});
</script>

<svelte:head>
	<title>G Vault | Dashboard</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="dashboard" />

	<div class="main-content">
		<!-- Top Status Bar -->
		<div class="status-bar">
			<span class="font-label" style="color: var(--color-on-surface-variant);">
				<span class="status-dot"></span>
				{pendingDepositCount > 0
					? `${pendingDepositCount} deposit request${pendingDepositCount > 1 ? 's' : ''} awaiting confirmation`
					: 'Live ledger synchronized'}
			</span>
			<button class="btn-ghost" onclick={() => (showDepositModal = true)}>
				<span class="material-icons" style="font-size: 15px;">add</span>
				Deposit Funds
			</button>
		</div>

		<div class="dashboard-body">
			<!-- Section Header -->
			<div class="section-header animate-fade-up stagger-1">
				<h1 class="font-display" style="margin: 0;">MEMBER<br />OVERVIEW</h1>
				<div>
					<p class="font-label" style="margin: 0 0 4px;">Welcome back</p>
					<p style="font-size: 1.125rem; font-weight: 700; margin: 0; color: var(--color-on-surface);">{memberName}</p>
					<span class="badge" style="margin-top: 8px;">Premium Member</span>
				</div>
			</div>

			{#if loadError}
				<p class="text-error" style="margin: 0;">{loadError}</p>
			{/if}

			<!-- Stat Cards -->
			<div class="stats-row animate-fade-up stagger-2">
				<div class="stat-block">
					<p class="stat-label">Savings Balance</p>
					<p class="stat-big">{formatMoney(savingsBalance)}</p>
					<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0; display: flex; align-items: center; gap: 4px;">
						<span class="material-icons" style="font-size: 14px; color: #1a7f37;">trending_up</span>
						{isLoading ? 'Refreshing...' : 'Updated from live ledger'}
					</p>
				</div>

				<div class="stat-block" style="background: var(--color-surface-container);">
					<p class="stat-label">Loan Balance</p>
					<p class="stat-big" style="font-size: 2rem;">{formatMoney(loanBalance)}</p>
					<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0;">
						{loanCardNote}
					</p>
				</div>

				<div class="stat-block" style="background: var(--color-surface-container-low);">
					<p class="stat-label">Next Repayment</p>
					<p class="stat-big" style="font-size: 2rem;">{formatMoney(estimatedMonthlyRepayment)}</p>
					<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0;">
						{hasNextRepayment ? `Due ${nextRepaymentDateLabel}` : nextRepaymentDateLabel}
					</p>
				</div>

				<div class="stat-block" style="background: var(--color-primary); color: var(--color-on-primary-container);">
					<p class="stat-label" style="color: rgba(255,255,255,0.6);">Pending Deposits</p>
					<p class="stat-big" style="color: white; font-size: 2rem;">{formatMoney(pendingDepositAmount)}</p>
					<p style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin: 8px 0 0;">
						{pendingDepositCount} awaiting mobile money confirmation
					</p>
				</div>
			</div>

			<!-- Loan Repayment Progress -->
			<div class="animate-fade-up stagger-3" style="background: var(--color-surface-container-lowest); padding: 32px;">
				<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 20px;">
					<div>
						<p class="font-label" style="margin: 0 0 6px;">Loan Repayment Progress</p>
						<p style="margin: 0; font-size: 0.875rem; color: var(--color-on-surface-variant);">{loanProgressMeta}</p>
					</div>
					<span style="font-size: 1rem; font-weight: 700; color: var(--color-on-surface);">{loanProgressPercent.toFixed(1)}%</span>
				</div>
				<div class="progress-bar" style="height: 4px;">
					<div class="progress-fill" style={`width: ${loanProgressPercent.toFixed(1)}%;`}></div>
				</div>
				<div style="display: flex; justify-content: space-between; margin-top: 12px;">
					<span class="font-label">{formatMoney(loanPaidAmount)} paid</span>
					<span class="font-label">{formatMoney(loanRemainingAmount)} remaining</span>
				</div>
			</div>

			<!-- Recent Transactions -->
			<div class="animate-fade-up stagger-4">
				<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0; padding: 0;">
					<h2 class="font-headline-md" style="margin: 0;">Recent Transactions</h2>
					<a href="/dashboard/statement" class="btn-ghost">
						View Full Statement
						<span class="material-icons" style="font-size: 14px;">arrow_forward</span>
					</a>
				</div>

				<div style="margin-top: 24px;">
					{#each transactions as tx}
						<div class="tx-row" style="border-bottom: 1px solid var(--color-surface-container-high);">
							<div style="display: flex; align-items: center; gap: 16px;">
								<div style="width: 40px; height: 40px; background: var(--color-surface-container-high); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
									<span class="material-icons" style="font-size: 16px; color: var(--color-on-surface-variant);">
										{#if tx.type === 'credit'}receipt{:else if tx.type === 'transfer'}swap_horiz{:else}shopping_bag{/if}
									</span>
								</div>
								<div>
									<p style="margin: 0; font-size: 0.875rem; font-weight: 600; letter-spacing: 0.01em; color: var(--color-on-surface);">{tx.merchant}</p>
									<p style="margin: 4px 0 0; font-size: 0.75rem; color: var(--color-on-surface-variant);">{tx.category} · {tx.date}</p>
								</div>
							</div>
							<div style="text-align: right;">
								<p style="margin: 0; font-size: 0.9375rem; font-weight: 700; color: {tx.type === 'credit' ? '#1a7f37' : 'var(--color-on-surface)'};">
									{formatAmount(tx.amount)}
								</p>
								<span
									class="badge {transactionBadgeClass(tx)}"
									style="margin-top: 4px;"
								>
									{tx.status}
								</span>
							</div>
						</div>
					{/each}
					{#if transactions.length === 0}
						<p style="margin: 16px 0 0; color: var(--color-on-surface-variant);">
							{isLoading ? 'Loading recent transactions...' : 'No recent transactions found.'}
						</p>
					{/if}
				</div>
			</div>

			<!-- Quick Actions -->
			<div class="quick-actions animate-fade-up stagger-5">
				<p class="font-label" style="margin: 0 0 20px;">Quick Actions</p>
				<div class="actions-grid">
					<a href="/dashboard/loans" class="action-card">
						<span class="material-icons action-icon">account_balance</span>
						<p class="action-label">Apply for Loan</p>
					</a>
					<button class="action-card" onclick={() => (showDepositModal = true)}>
						<span class="material-icons action-icon">add_card</span>
						<p class="action-label">Deposit Funds</p>
					</button>
					<a href="/dashboard/transfer" class="action-card">
						<span class="material-icons action-icon">swap_horiz</span>
						<p class="action-label">Transfer</p>
					</a>
					<a href="/dashboard/statement" class="action-card">
						<span class="material-icons action-icon">receipt_long</span>
						<p class="action-label">Statement</p>
					</a>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<footer class="footer">
			<p class="font-label" style="margin: 0;">© 2026 G VAULT</p>
			<div class="footer-links">
				<a href="/legal/privacy" class="footer-link">Privacy</a>
				<a href="/legal/terms" class="footer-link">Terms</a>
				<a href="/legal/security" class="footer-link">Security</a>
				<a href="/legal/accessibility" class="footer-link">Accessibility</a>
			</div>
		</footer>
	</div>
</div>

{#if showDepositModal}
	<DepositModal onclose={() => (showDepositModal = false)} onsuccess={loadDashboard} />
{/if}

<style>
	.page-wrap {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background-color: var(--color-surface);
	}

	.status-bar {
		background-color: var(--color-surface-container-low);
		padding: 12px 40px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-bottom: none;
	}

	.status-dot {
		display: inline-block;
		width: 6px;
		height: 6px;
		background: #1a7f37;
		border-radius: 50% !important;
		margin-right: 8px;
		vertical-align: middle;
		animation: pulse 2s ease infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.4; }
	}

	.dashboard-body {
		padding: 56px 40px;
		display: flex;
		flex-direction: column;
		gap: 40px;
		flex: 1;
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.stats-row {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 2px;
	}

	.quick-actions {
		background: var(--color-surface-container-lowest);
		padding: 32px;
	}

	.actions-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 2px;
	}

	.action-card {
		background: var(--color-surface-container-low);
		padding: 24px;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 12px;
		text-decoration: none;
		border: none;
		cursor: pointer;
		font-family: var(--font-family);
		transition: background-color 0.15s ease;
		text-align: left;
	}

	.action-card:hover {
		background: var(--color-surface-container);
	}

	.action-icon {
		font-size: 20px !important;
		color: var(--color-on-surface-variant);
	}

	.action-label {
		margin: 0;
		font-size: 0.6875rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-on-surface);
	}

	@media (max-width: 1024px) {
		.stats-row { grid-template-columns: repeat(2, 1fr); }
		.actions-grid { grid-template-columns: repeat(2, 1fr); }
		.section-header { flex-direction: column; gap: 24px; }
	}

	@media (max-width: 640px) {
		.dashboard-body { padding: 32px 20px; }
		.stats-row { grid-template-columns: 1fr; }
		.actions-grid { grid-template-columns: repeat(2, 1fr); }
	}
</style>
