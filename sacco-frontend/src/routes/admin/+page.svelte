<script lang="ts">
	import AdminSidebar from '$lib/components/AdminSidebar.svelte';

	let activeSection = $state<'overview' | 'users' | 'analytics' | 'lending' | 'audit' | 'settings'>('overview');

	const pendingApplications = [
		{ id: 'LN-2024-10481', name: 'Amara Osei', amount: 25000, type: 'Business Loan', submitted: '2025-04-11', score: 724, status: 'pending' },
		{ id: 'LN-2024-10482', name: 'Sofia Marchetti', amount: 10000, type: 'Personal Loan', submitted: '2025-04-10', score: 802, status: 'pending' },
		{ id: 'LN-2024-10483', name: 'Keanu Reeves-Walsh', amount: 50000, type: 'Real Estate', submitted: '2025-04-09', score: 688, status: 'pending' },
		{ id: 'LN-2024-10484', name: 'Priya Nair', amount: 8000, type: 'Education', submitted: '2025-04-08', score: 756, status: 'pending' },
	];

	const systemStats = {
		totalMembers: 3842,
		activeLoans: 1024,
		totalDeposits: 18420000,
		loanBook: 7350000,
		npRatio: 2.4,
		caseQueue: 4,
	};

	type ApplicationId = string;
	let actionStates = $state<Record<ApplicationId, 'approving' | 'rejecting' | 'approved' | 'rejected' | undefined>>({});

	async function handleAction(id: string, action: 'approve' | 'reject') {
		actionStates[id] = action === 'approve' ? 'approving' : 'rejecting';
		await new Promise((r) => setTimeout(r, 1000));
		actionStates[id] = action === 'approve' ? 'approved' : 'rejected';
	}

	function f(n: number) {
		return Math.round(n).toLocaleString('en-UG');
	}
</script>

<svelte:head>
	<title>G Vault Admin Terminal</title>
</svelte:head>

<div style="display: flex; min-height: 100vh; background: var(--color-surface-container-low);">
	<AdminSidebar active={activeSection} onchange={(s) => (activeSection = s)} />

	<div class="admin-main">
		<!-- Top bar -->
		<div class="admin-topbar">
			<div>
				<p class="font-label" style="margin: 0; color: var(--color-on-surface-variant);">Terminal v1.0</p>
				<p style="margin: 0; font-size: 0.875rem; font-weight: 600; color: var(--color-on-surface); text-transform: uppercase; letter-spacing: 0.05em;">
					{activeSection === 'overview' ? 'System Overview' :
					 activeSection === 'users' ? 'User Management' :
					 activeSection === 'analytics' ? 'Analytics' :
					 activeSection === 'lending' ? 'Lending Queue' :
					 activeSection === 'audit' ? 'Audit Log' : 'Settings'}
				</p>
			</div>
			<div style="display: flex; align-items: center; gap: 16px;">
				<span style="display: flex; align-items: center; gap: 6px; font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: var(--color-on-surface-variant);">
					<span style="width: 6px; height: 6px; background: #1a7f37; border-radius: 50% !important; display: inline-block;"></span>
					Systems Nominal
				</span>
				<a href="/" class="btn-ghost" style="font-size: 0.6875rem;">
					<span class="material-icons" style="font-size: 14px;">logout</span>
					Sign Out
				</a>
			</div>
		</div>

		<div class="admin-body">

			<!-- System KPIs -->
			<div class="kpi-grid animate-fade-up stagger-1">
				{#each [
					{ label: 'Total Members', value: systemStats.totalMembers.toLocaleString(), icon: 'group', trend: '+12 this week' },
					{ label: 'Active Loans', value: systemStats.activeLoans.toLocaleString(), icon: 'account_balance', trend: '81.2% utilization' },
					{ label: 'Total Deposits', value: 'UGX ' + (systemStats.totalDeposits / 1e6).toFixed(2) + 'M', icon: 'savings', trend: '+UGX 240K this month' },
					{ label: 'Loan Book', value: 'UGX ' + (systemStats.loanBook / 1e6).toFixed(2) + 'M', icon: 'receipt_long', trend: 'NPL: ' + systemStats.npRatio + '%' },
					{ label: 'Case Queue', value: String(systemStats.caseQueue), icon: 'pending_actions', trend: 'Avg. 18h resolution' },
					{ label: 'System Uptime', value: '99.98%', icon: 'monitoring', trend: 'Last incident: 42d ago' },
				] as kpi}
					<div class="kpi-card">
						<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
							<p class="stat-label" style="margin: 0;">{kpi.label}</p>
							<span class="material-icons" style="font-size: 18px; color: var(--color-on-surface-variant);">{kpi.icon}</span>
						</div>
						<p class="stat-value" style="margin: 0 0 8px; font-size: 1.75rem;">{kpi.value}</p>
						<p style="margin: 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{kpi.trend}</p>
					</div>
				{/each}
			</div>

			<!-- Pending Applications Queue -->
			<div class="animate-fade-up stagger-2">
				<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
					<div>
						<p class="font-label" style="margin: 0 0 4px;">System Queue</p>
						<h2 class="font-headline-md" style="margin: 0;">User Applications</h2>
					</div>
					<span class="badge">{pendingApplications.length} Pending</span>
				</div>

				<div class="applications-table">
					<table class="data-table">
						<thead>
							<tr>
								<th>Application ID</th>
								<th>Applicant</th>
								<th>Loan Type</th>
								<th>Amount</th>
								<th>Credit Score</th>
								<th>Submitted</th>
								<th>Status</th>
								<th>Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each pendingApplications as app}
								{@const state = actionStates[app.id]}
								<tr class:row-approved={state === 'approved'} class:row-rejected={state === 'rejected'}>
									<td style="font-weight: 700; font-size: 0.75rem; letter-spacing: 0.04em;">{app.id}</td>
									<td style="font-weight: 600;">{app.name}</td>
									<td style="color: var(--color-on-surface-variant);">{app.type}</td>
									<td style="font-weight: 700;">UGX {f(app.amount)}</td>
									<td>
										<span style="font-weight: 700; color: {app.score >= 750 ? '#1a7f37' : app.score >= 700 ? 'var(--color-on-surface)' : 'var(--color-error)'};">
											{app.score}
										</span>
									</td>
									<td style="color: var(--color-on-surface-variant);">{app.submitted}</td>
									<td>
										{#if state === 'approved'}
											<span class="badge badge-success">Approved</span>
										{:else if state === 'rejected'}
											<span class="badge badge-error">Rejected</span>
										{:else}
											<span class="badge badge-pending">Pending Review</span>
										{/if}
									</td>
									<td>
										{#if !state || (state !== 'approved' && state !== 'rejected')}
											<div style="display: flex; gap: 8px;">
												<button
													class="btn-primary"
													style="padding: 8px 16px; font-size: 0.6rem;"
													disabled={state === 'approving' || state === 'rejecting'}
													onclick={() => handleAction(app.id, 'approve')}
												>
													{state === 'approving' ? '...' : 'Approve'}
												</button>
												<button
													class="btn-secondary"
													style="padding: 8px 16px; font-size: 0.6rem; background: var(--color-error-container); color: var(--color-error);"
													disabled={state === 'approving' || state === 'rejecting'}
													onclick={() => handleAction(app.id, 'reject')}
												>
													{state === 'rejecting' ? '...' : 'Reject'}
												</button>
											</div>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Recent Activity Log -->
			<div class="animate-fade-up stagger-3" style="background: var(--color-surface-container-lowest); padding: 32px;">
				<p class="font-label" style="margin: 0 0 20px;">Recent System Events</p>
				{#each [
					{ time: '08:42:15', event: 'Member login authenticated', user: 'julian.thorne@email.com', type: 'info' },
					{ time: '08:39:02', event: 'Loan application submitted', user: 'amara.osei@email.com', type: 'action' },
					{ time: '08:35:47', event: 'Automated repayment processed', user: 'system', type: 'system' },
					{ time: '08:22:11', event: 'New member account created', user: 'sofia.marchetti@email.com', type: 'info' },
					{ time: '08:10:00', event: 'Daily report generated', user: 'system', type: 'system' },
				] as event}
					<div style="display: flex; align-items: flex-start; gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--color-surface-container);">
						<span style="font-size: 0.6875rem; font-weight: 600; color: var(--color-on-surface-variant); min-width: 72px; padding-top: 1px; font-family: monospace; letter-spacing: 0.04em;">{event.time}</span>
						<div>
							<p style="margin: 0; font-size: 0.8125rem; font-weight: 500; color: var(--color-on-surface);">{event.event}</p>
							<p style="margin: 2px 0 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{event.user}</p>
						</div>
						<span class="badge {event.type === 'action' ? '' : event.type === 'system' ? '' : ''}" style="margin-left: auto; flex-shrink: 0;">
							{event.type}
						</span>
					</div>
				{/each}
			</div>
		</div>

		<footer class="footer" style="background: var(--color-surface-container);">
			<p class="font-label" style="margin: 0;">© 2024 G VAULT — ADMIN TERMINAL</p>
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
	.admin-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background: var(--color-surface);
		overflow-x: auto;
	}

	.admin-topbar {
		background: var(--color-surface-container-lowest);
		padding: 16px 40px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		position: sticky;
		top: 0;
		z-index: 50;
	}

	.admin-body {
		padding: 48px 40px;
		display: flex;
		flex-direction: column;
		gap: 40px;
		flex: 1;
	}

	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 2px;
	}

	.kpi-card {
		background: var(--color-surface-container-lowest);
		padding: 24px 20px;
		transition: background-color 0.15s ease;
	}

	.kpi-card:hover {
		background: var(--color-surface-container-low);
	}

	.applications-table {
		overflow-x: auto;
	}

	:global(.row-approved td) {
		background-color: #f0faf4 !important;
	}

	:global(.row-rejected td) {
		background-color: var(--color-error-container) !important;
		opacity: 0.7;
	}

	@media (max-width: 1280px) {
		.kpi-grid { grid-template-columns: repeat(3, 1fr); }
	}

	@media (max-width: 768px) {
		.admin-body { padding: 24px 16px; }
		.kpi-grid { grid-template-columns: repeat(2, 1fr); }
		.admin-topbar { padding: 12px 16px; }
	}
</style>
