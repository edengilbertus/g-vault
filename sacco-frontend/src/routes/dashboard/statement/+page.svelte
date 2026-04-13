<script lang="ts">
	import MemberNav from '$lib/components/MemberNav.svelte';

	const allTransactions = [
		{ id: 'T008', merchant: 'SALARY DEPOSIT', category: 'Direct Deposit', amount: 8500.00, date: 'Apr 25, 2024', time: '09:00', type: 'credit', status: 'completed' },
		{ id: 'T007', merchant: 'MORTGAGE PAYMENT', category: 'Housing', amount: -2100.00, date: 'Apr 20, 2024', time: '14:30', type: 'debit', status: 'completed' },
		{ id: 'T006', merchant: 'WIRE TRANSFER OUT', category: 'Transfer', amount: -500.00, date: 'Apr 18, 2024', time: '11:15', type: 'transfer', status: 'completed' },
		{ id: 'T001', merchant: 'APPLE STORE — METROPOLIS', category: 'Electronic Equipment', amount: -1299.00, date: 'Apr 12, 2024', time: '16:45', type: 'debit', status: 'completed' },
		{ id: 'T002', merchant: 'LOAN REPAYMENT — AUTO', category: 'Recurring Transaction', amount: -1250.00, date: 'Apr 10, 2024', time: '01:00', type: 'debit', status: 'completed' },
		{ id: 'T003', merchant: 'GLOBAL TECH CORP SALARY', category: 'Direct Deposit', amount: 8500.00, date: 'Apr 05, 2024', time: '09:00', type: 'credit', status: 'completed' },
		{ id: 'T004', merchant: 'VERIDIAN UTILITIES', category: 'Bill Payment', amount: -245.80, date: 'Apr 03, 2024', time: '10:20', type: 'debit', status: 'completed' },
		{ id: 'T005', merchant: 'INTERNAL TRANSFER TO SAVINGS', category: 'Automated Vault', amount: -2000.00, date: 'Apr 01, 2024', time: '23:55', type: 'transfer', status: 'completed' },
	];

	let filterType = $state('all'); // 'all', 'credit', 'debit', 'transfer'

	let filteredTransactions = $derived(
		filterType === 'all' ? allTransactions : allTransactions.filter(t => t.type === filterType)
	);

	function formatAmount(n: number) {
		const abs = Math.round(Math.abs(n)).toLocaleString('en-UG');
		return (n >= 0 ? '+' : '−') + ' UGX ' + abs;
	}
</script>

<svelte:head>
	<title>G Vault | Statement</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="dashboard" /> <!-- Nav uses exact id from links array, keeping highlight clear -> could add 'statement' to it, but for now we follow schema -->

	<div class="main-content">
		<div class="dashboard-body">
			<div class="section-header animate-fade-up stagger-1">
				<h1 class="font-display" style="margin: 0;">ACCOUNT<br />STATEMENT</h1>
				<div style="text-align: right;">
					<button class="btn-secondary" style="margin-bottom: 8px;">
						<span class="material-icons" style="font-size: 16px;">download</span>
						Export PDF
					</button>
					<button class="btn-ghost">
						<span class="material-icons" style="font-size: 16px;">download</span>
						Export CSV
					</button>
				</div>
			</div>

			<div class="animate-fade-up stagger-2" style="margin-top: 32px;">
				<div style="display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap;">
					<button class="filter-chip {filterType === 'all' ? 'active' : ''}" onclick={() => filterType = 'all'}>All Transactions</button>
					<button class="filter-chip {filterType === 'credit' ? 'active' : ''}" onclick={() => filterType = 'credit'}>Credits In</button>
					<button class="filter-chip {filterType === 'debit' ? 'active' : ''}" onclick={() => filterType = 'debit'}>Debits Out</button>
					<button class="filter-chip {filterType === 'transfer' ? 'active' : ''}" onclick={() => filterType = 'transfer'}>Transfers</button>
				</div>

				<div class="statement-table-wrapper">
					<table class="data-table">
						<thead>
							<tr>
								<th>Date & Time</th>
								<th>Description & Category</th>
								<th>Reference</th>
								<th style="text-align: right;">Amount</th>
							</tr>
						</thead>
						<tbody>
							{#each filteredTransactions as tx}
								<tr>
									<td style="white-space: nowrap;">
										<p style="margin: 0; font-weight: 600;">{tx.date}</p>
										<p style="margin: 2px 0 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{tx.time}</p>
									</td>
									<td>
										<p style="margin: 0; font-weight: 600; font-size: 0.8125rem;">{tx.merchant}</p>
										<p style="margin: 2px 0 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{tx.category}</p>
									</td>
									<td style="font-family: monospace; font-size: 0.75rem; color: var(--color-on-surface-variant);">{tx.id}</td>
									<td style="text-align: right;">
										<p style="margin: 0; font-weight: 700; color: {tx.type === 'credit' ? '#1a7f37' : 'var(--color-on-surface)'};">
											{formatAmount(tx.amount)}
										</p>
										<span class="badge {tx.type === 'credit' ? 'badge-success' : tx.type === 'transfer' ? '' : 'badge-pending'}" style="margin-top: 4px; display: inline-block;">
											{tx.type}
										</span>
									</td>
								</tr>
							{/each}
							{#if filteredTransactions.length === 0}
								<tr>
									<td colspan="4" style="text-align: center; padding: 48px; color: var(--color-on-surface-variant);">
										No transactions found for this filter.
									</td>
								</tr>
							{/if}
						</tbody>
					</table>
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

<style>
	.page-wrap {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background-color: var(--color-surface);
	}

	.dashboard-body {
		padding: 56px 40px;
		display: flex;
		flex-direction: column;
		flex: 1;
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
	}

	.filter-chip {
		padding: 8px 16px;
		border: 1px solid var(--color-outline-variant);
		background: transparent;
		color: var(--color-on-surface-variant);
		font-family: var(--font-family);
		font-size: 0.75rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.filter-chip:hover {
		background: var(--color-surface-container);
	}

	.filter-chip.active {
		background: var(--color-on-surface);
		color: var(--color-surface);
		border-color: var(--color-on-surface);
	}

	.statement-table-wrapper {
		overflow-x: auto;
		background: var(--color-surface-container-lowest);
		border: 1px solid var(--color-surface-container-high);
	}

	@media (max-width: 768px) {
		.dashboard-body { padding: 32px 20px; }
		.section-header { flex-direction: column; align-items: flex-start; gap: 24px; }
	}
</style>
