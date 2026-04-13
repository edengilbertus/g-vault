<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { fetchDashboardSummary, fetchMyLoanAccounts } from '$lib/api/client';
	import { getStoredToken } from '$lib/auth/session';
	import MemberNav from '$lib/components/MemberNav.svelte';

	type AccountView = {
		id: string;
		name: string;
		type: string;
		balance: number;
		currency: 'UGX';
		status: 'Active' | 'Locked' | 'Closed';
		rate?: string;
	};

	let accounts = $state<AccountView[]>([]);
	let totalLiquidAssets = $state(0);
	let isLoading = $state(true);
	let loadError = $state('');

	function f(n: number) {
		return Math.round(n).toLocaleString('en-UG');
	}

	async function loadAccounts() {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		isLoading = true;
		loadError = '';
		try {
			const [summary, loanAccounts] = await Promise.all([
				fetchDashboardSummary(token),
				fetchMyLoanAccounts(token)
			]);

			const savingsBalance = Number(summary.savings_balance);
			totalLiquidAssets = savingsBalance;
			const loanList = Array.isArray(loanAccounts) ? loanAccounts : (loanAccounts as any).results || [];
			accounts = [
				{
					id: 'ACC-001',
					name: 'Main Savings',
					type: 'Savings',
					balance: savingsBalance,
					currency: 'UGX',
					status: 'Active'
				},
				...loanList.map((loan: any) => ({
					id: `LN-${String(loan.application_id).padStart(5, '0')}`,
					name: 'Loan Account',
					type: `Loan (${loan.term_months} months)`,
					balance: Number(loan.outstanding_balance),
					currency: 'UGX' as const,
					status: loan.status === 'active' ? 'Active' : loan.status === 'closed' ? 'Closed' : 'Locked'
				}))
			];
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'Unable to load account portfolio.';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		void loadAccounts();
	});
</script>

<svelte:head>
	<title>G Vault | Accounts</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="accounts" />

	<div class="main-content">
		<!-- Top Status Bar -->
		<div class="status-bar">
			<span class="font-label" style="color: var(--color-on-surface-variant);">
				<span class="status-dot"></span>
				System Latency: 14ms
			</span>
		</div>

		<div class="dashboard-body">
			<!-- Section Header -->
			<div class="section-header animate-fade-up stagger-1">
				<h1 class="font-display" style="margin: 0;">ACCOUNT<br />PORTFOLIO</h1>
				<div>
					<p class="font-label" style="margin: 0 0 4px;">Total Liquid Assets</p>
					<p style="font-size: 1.5rem; font-weight: 700; margin: 0; color: var(--color-on-surface);">UGX {f(totalLiquidAssets)}</p>
				</div>
			</div>

			<!-- Accounts List -->
			<div class="animate-fade-up stagger-2">
				{#if loadError}
					<p class="text-error" style="margin: 0 0 16px;">{loadError}</p>
				{/if}
				<div class="accounts-grid">
					{#each accounts as acc}
						<div class="account-card">
							<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
								<div>
									<p class="font-label" style="margin: 0 0 4px;">{acc.type}</p>
									<h3 style="margin: 0; font-size: 1.125rem; font-weight: 700; color: var(--color-on-surface);">{acc.name}</h3>
									<p style="margin: 4px 0 0; font-size: 0.75rem; font-family: monospace; color: var(--color-on-surface-variant);">{acc.id}</p>
								</div>
								<span class="badge {acc.status === 'Active' ? 'badge-success' : 'badge-pending'}">{acc.status}</span>
							</div>
							
							<div style="margin-top: auto;">
								<p class="font-label" style="margin: 0 0 4px; color: var(--color-on-surface-variant);">Available Balance</p>
								<p style="margin: 0; font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; color: var(--color-on-surface);">
									<span style="font-size: 1rem; font-weight: 600; vertical-align: top; margin-right: 4px;">UGX</span> {f(acc.balance)}
								</p>
								{#if acc.rate}
									<p style="margin: 8px 0 0; font-size: 0.75rem; color: #1a7f37; font-weight: 600;">Yield: {acc.rate} APY</p>
								{/if}
							</div>

							<div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--color-surface-container-high); display: flex; justify-content: flex-end;">
								<button class="btn-ghost" style="padding: 4px 8px; font-size: 0.6875rem;">View Details <span class="material-icons" style="font-size: 14px; margin-left: 4px;">arrow_forward</span></button>
							</div>
						</div>
					{/each}
					{#if accounts.length === 0}
						<div class="account-card" style="grid-column: 1 / -1; text-align: center;">
							<p style="margin: 0; color: var(--color-on-surface-variant);">
								{isLoading ? 'Loading account portfolio...' : 'No accounts available.'}
							</p>
						</div>
					{/if}
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

	.accounts-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 24px;
	}

	.account-card {
		background: var(--color-surface-container-lowest);
		padding: 32px;
		display: flex;
		flex-direction: column;
		border: 1px solid var(--color-surface-container-high);
		transition: border-color 0.2s ease, background-color 0.2s ease;
	}

	.account-card:hover {
		background: var(--color-surface-container-low);
		border-color: var(--color-primary);
	}

	@media (max-width: 1024px) {
		.accounts-grid { grid-template-columns: repeat(2, 1fr); }
	}

	@media (max-width: 768px) {
		.accounts-grid { grid-template-columns: 1fr; }
		.dashboard-body { padding: 32px 20px; }
		.section-header { flex-direction: column; gap: 24px; }
	}
</style>
