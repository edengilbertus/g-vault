<script lang="ts">
	import { page } from '$app/state';
	import DepositModal from '$lib/components/DepositModal.svelte';
	import MemberNav from '$lib/components/MemberNav.svelte';

	let showDepositModal = $state(false);

	const transactions = [
		{ id: 'T001', merchant: 'APPLE STORE — METROPOLIS', category: 'Electronic Equipment', amount: -1299.00, date: 'Apr 12', type: 'debit' },
		{ id: 'T002', merchant: 'LOAN REPAYMENT — AUTO', category: 'Recurring Transaction', amount: -1250.00, date: 'Apr 10', type: 'debit' },
		{ id: 'T003', merchant: 'GLOBAL TECH CORP SALARY', category: 'Direct Deposit', amount: +8500.00, date: 'Apr 05', type: 'credit' },
		{ id: 'T004', merchant: 'VERIDIAN UTILITIES', category: 'Bill Payment', amount: -245.80, date: 'Apr 03', type: 'debit' },
		{ id: 'T005', merchant: 'INTERNAL TRANSFER TO SAVINGS', category: 'Automated Vault', amount: -2000.00, date: 'Apr 01', type: 'transfer' },
	];

	function formatAmount(n: number) {
		const abs = Math.round(Math.abs(n)).toLocaleString('en-UG');
		return (n >= 0 ? '+' : '−') + ' UGX ' + abs;
	}
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
				System Latency: 12ms — Last Login: Today 08:42 GMT
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
					<p style="font-size: 1.125rem; font-weight: 700; margin: 0; color: var(--color-on-surface);">Julian Thorne</p>
					<span class="badge" style="margin-top: 8px;">Premium Member</span>
				</div>
			</div>

			<!-- Stat Cards -->
			<div class="stats-row animate-fade-up stagger-2">
				<div class="stat-block">
					<p class="stat-label">Savings Balance</p>
					<p class="stat-big">UGX 142,850</p>
					<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0; display: flex; align-items: center; gap: 4px;">
						<span class="material-icons" style="font-size: 14px; color: #1a7f37;">trending_up</span>
						+4.2% this month
					</p>
				</div>

				<div class="stat-block" style="background: var(--color-surface-container);">
					<p class="stat-label">Loan Balance</p>
					<p class="stat-big" style="font-size: 2rem;">UGX 45,000</p>
					<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0;">
						18% APR · 24 months
					</p>
				</div>

				<div class="stat-block" style="background: var(--color-surface-container-low);">
					<p class="stat-label">Next Repayment</p>
					<p class="stat-big" style="font-size: 2rem;">UGX 1,250</p>
					<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0;">Due Apr 30, 2025</p>
				</div>

				<div class="stat-block" style="background: var(--color-primary); color: var(--color-on-primary-container);">
					<p class="stat-label" style="color: rgba(255,255,255,0.6);">Credit Score</p>
					<p class="stat-big" style="color: white; font-size: 2rem;">782</p>
					<p style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin: 8px 0 0;">Excellent</p>
				</div>
			</div>

			<!-- Loan Repayment Progress -->
			<div class="animate-fade-up stagger-3" style="background: var(--color-surface-container-lowest); padding: 32px;">
				<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 20px;">
					<div>
						<p class="font-label" style="margin: 0 0 6px;">Loan Repayment Progress</p>
						<p style="margin: 0; font-size: 0.875rem; color: var(--color-on-surface-variant);">Disbursed Jan 2024 · 24-month term</p>
					</div>
					<span style="font-size: 1rem; font-weight: 700; color: var(--color-on-surface);">62.5%</span>
				</div>
				<div class="progress-bar" style="height: 4px;">
					<div class="progress-fill" style="width: 62.5%;"></div>
				</div>
				<div style="display: flex; justify-content: space-between; margin-top: 12px;">
					<span class="font-label">UGX 28,125 paid</span>
					<span class="font-label">UGX 16,875 remaining</span>
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
					{#each transactions as tx, i}
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
								<span class="badge {tx.type === 'credit' ? 'badge-success' : tx.type === 'transfer' ? '' : 'badge-pending'}" style="margin-top: 4px;">
									{tx.type}
								</span>
							</div>
						</div>
					{/each}
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
			<p class="font-label" style="margin: 0;">© 2024 G VAULT</p>
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
	<DepositModal onclose={() => (showDepositModal = false)} />
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
