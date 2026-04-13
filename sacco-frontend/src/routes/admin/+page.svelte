<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import AdminSidebar from '$lib/components/AdminSidebar.svelte';
	import {
		decideLoanApplication,
		fetchAdminActivity,
		fetchAdminOverview,
		fetchAdminPendingLoans,
		type AdminActivityEventApi,
		type LoanApplicationApi
	} from '$lib/api/client';
	import { getStoredToken } from '$lib/auth/session';

	let activeSection = $state<'overview' | 'users' | 'analytics' | 'lending' | 'audit' | 'settings'>('overview');

	type PendingApplication = {
		applicationId: number;
		id: string;
		name: string;
		amount: number;
		type: string;
		submitted: string;
		status: 'pending' | 'approved' | 'rejected';
	};

	let pendingApplications = $state<PendingApplication[]>([]);
	let recentEvents = $state<AdminActivityEventApi[]>([]);
	let isLoading = $state(true);
	let loadError = $state('');

	let systemStats = $state({
		totalMembers: 0,
		activeLoans: 0,
		totalDeposits: 0,
		loanBook: 0,
		npRatio: 0,
		caseQueue: 0,
		totalTransactions: 0,
		totalNotifications: 0,
		failedNotifications: 0
	});

	type ApplicationId = string;
	let actionStates = $state<Record<ApplicationId, 'approving' | 'rejecting' | 'approved' | 'rejected' | undefined>>({});
	let pendingCount = $derived(pendingApplications.filter((app) => app.status === 'pending').length);
	let userEvents = $derived(recentEvents.filter((event) => event.event_type === 'user.joined'));
	let lendingEvents = $derived(recentEvents.filter((event) => event.event_type.startsWith('loan.')));
	let transactionEvents = $derived(recentEvents.filter((event) => event.event_type.startsWith('transaction.')));
	let notificationEvents = $derived(recentEvents.filter((event) => event.event_type.startsWith('sms.')));

	function formatApplicationId(id: number): string {
		return `LN-${new Date().getFullYear()}-${String(id).padStart(5, '0')}`;
	}

	function getLoanType(purpose: string): string {
		if (purpose === 'business') return 'Business Loan';
		if (purpose === 'education') return 'Education Loan';
		if (purpose === 'medical') return 'Medical Loan';
		if (purpose === 'real_estate') return 'Real Estate';
		return 'Personal Loan';
	}

	async function loadAdminData() {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		isLoading = true;
		loadError = '';
		try {
			const [overview, pending, activity] = await Promise.all([
				fetchAdminOverview(token),
				fetchAdminPendingLoans(token),
				fetchAdminActivity(token, 12)
			]);

			systemStats = {
				totalMembers: overview.total_members,
				activeLoans: overview.active_loans,
				totalDeposits: Number(overview.total_deposits),
				loanBook: Number(overview.loan_book),
				npRatio: Number(overview.np_ratio),
				caseQueue: overview.case_queue,
				totalTransactions: overview.total_transactions,
				totalNotifications: overview.total_notifications,
				failedNotifications: overview.failed_notifications
			};

			pendingApplications = pending.map((app: LoanApplicationApi) => ({
				applicationId: app.id,
				id: formatApplicationId(app.id),
				name: app.member_name || 'Admin',
				amount: Number(app.amount),
				type: getLoanType(app.purpose),
				submitted: new Date(app.created_at).toISOString().slice(0, 10),
				status: app.status as PendingApplication['status']
			}));
			recentEvents = activity;
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'Failed to load admin dashboard data.';
		} finally {
			isLoading = false;
		}
	}

	async function handleAction(applicationId: number, action: 'approve' | 'reject') {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		const idKey = String(applicationId);
		actionStates[idKey] = action === 'approve' ? 'approving' : 'rejecting';
		try {
			await decideLoanApplication(token, applicationId, { action });
			actionStates[idKey] = action === 'approve' ? 'approved' : 'rejected';
			pendingApplications = pendingApplications.map((app) =>
				app.applicationId === applicationId ? { ...app, status: action === 'approve' ? 'approved' : 'rejected' } : app
			);
			systemStats.caseQueue = pendingApplications.filter((app) => app.status === 'pending').length;
			await loadAdminData();
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'Unable to process loan decision.';
			actionStates[idKey] = undefined;
		}
	}

	function f(n: number) {
		return Math.round(n).toLocaleString('en-UG');
	}

	function formatEventTime(occurredAt: string) {
		return new Date(occurredAt).toLocaleTimeString('en-UG', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			hour12: false
		});
	}

	function formatEventDate(occurredAt: string) {
		return new Date(occurredAt).toLocaleDateString('en-UG', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function asPercent(value: number): string {
		return `${(value * 100).toFixed(1)}%`;
	}

	function notificationSuccessRatio(): number {
		if (systemStats.totalNotifications === 0) {
			return 1;
		}
		const successful = systemStats.totalNotifications - systemStats.failedNotifications;
		return Math.max(0, successful) / systemStats.totalNotifications;
	}

	onMount(() => {
		void loadAdminData();
	});
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
			</div>
		</div>

		<div class="admin-body">
			{#if loadError}
				<p class="text-error" style="margin: 0;">{loadError}</p>
			{/if}

			{#if activeSection === 'overview'}
				<div class="kpi-grid animate-fade-up stagger-1">
					{#each [
						{ label: 'Total Members', value: systemStats.totalMembers.toLocaleString(), icon: 'group', note: `${systemStats.totalMembers} registered accounts` },
						{ label: 'Active Loans', value: systemStats.activeLoans.toLocaleString(), icon: 'account_balance', note: `${systemStats.activeLoans} active loan accounts` },
						{ label: 'Total Deposits', value: 'UGX ' + (systemStats.totalDeposits / 1e6).toFixed(2) + 'M', icon: 'savings', note: `${systemStats.totalTransactions} total transactions` },
						{ label: 'Loan Book', value: 'UGX ' + (systemStats.loanBook / 1e6).toFixed(2) + 'M', icon: 'receipt_long', note: `NPL: ${systemStats.npRatio}%` },
						{ label: 'Case Queue', value: String(systemStats.caseQueue), icon: 'pending_actions', note: `${pendingCount} pending decisions` },
						{ label: 'Notifications', value: systemStats.totalNotifications.toLocaleString(), icon: 'sms', note: `${systemStats.failedNotifications} failed notifications` },
					] as kpi}
						<div class="kpi-card">
							<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
								<p class="stat-label" style="margin: 0;">{kpi.label}</p>
								<span class="material-icons" style="font-size: 18px; color: var(--color-on-surface-variant);">{kpi.icon}</span>
							</div>
							<p class="stat-value" style="margin: 0 0 8px; font-size: 1.75rem;">{kpi.value}</p>
							<p style="margin: 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{kpi.note}</p>
						</div>
					{/each}
				</div>

				<div class="animate-fade-up stagger-2">
					<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
						<div>
							<p class="font-label" style="margin: 0 0 4px;">System Queue</p>
							<h2 class="font-headline-md" style="margin: 0;">User Applications</h2>
						</div>
						<span class="badge">{pendingCount} Pending</span>
					</div>

					<div class="applications-table">
						<table class="data-table">
							<thead>
								<tr>
									<th>Application ID</th>
									<th>Applicant</th>
									<th>Loan Type</th>
									<th>Amount</th>
									<th>Submitted</th>
									<th>Status</th>
									<th>Actions</th>
								</tr>
							</thead>
							<tbody>
								{#each pendingApplications as app}
									{@const state =
										actionStates[String(app.applicationId)] ??
										(app.status === 'approved' ? 'approved' : app.status === 'rejected' ? 'rejected' : undefined)}
									<tr class:row-approved={state === 'approved'} class:row-rejected={state === 'rejected'}>
										<td style="font-weight: 700; font-size: 0.75rem; letter-spacing: 0.04em;">{app.id}</td>
										<td style="font-weight: 600;">{app.name}</td>
										<td style="color: var(--color-on-surface-variant);">{app.type}</td>
										<td style="font-weight: 700;">UGX {f(app.amount)}</td>
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
														onclick={() => handleAction(app.applicationId, 'approve')}
													>
														{state === 'approving' ? '...' : 'Approve'}
													</button>
													<button
														class="btn-secondary"
														style="padding: 8px 16px; font-size: 0.6rem; background: var(--color-error-container); color: var(--color-error);"
														disabled={state === 'approving' || state === 'rejecting'}
														onclick={() => handleAction(app.applicationId, 'reject')}
													>
														{state === 'rejecting' ? '...' : 'Reject'}
													</button>
												</div>
											{/if}
										</td>
									</tr>
								{/each}
								{#if pendingApplications.length === 0}
									<tr>
										<td colspan="7" style="text-align: center; color: var(--color-on-surface-variant);">
											{isLoading ? 'Loading pending applications...' : 'No pending loan applications.'}
										</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>

				<div class="animate-fade-up stagger-3" style="background: var(--color-surface-container-lowest); padding: 32px;">
					<p class="font-label" style="margin: 0 0 20px;">Recent System Events</p>
					{#each recentEvents as event}
						<div style="display: flex; align-items: flex-start; gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--color-surface-container);">
							<span style="font-size: 0.6875rem; font-weight: 600; color: var(--color-on-surface-variant); min-width: 72px; padding-top: 1px; font-family: monospace; letter-spacing: 0.04em;">{formatEventTime(event.occurred_at)}</span>
							<div>
								<p style="margin: 0; font-size: 0.8125rem; font-weight: 500; color: var(--color-on-surface);">{event.message}</p>
								<p style="margin: 2px 0 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{event.actor}</p>
							</div>
							<span class="badge {event.severity === 'info' ? 'badge-pending' : event.severity === 'action' ? 'badge-success' : ''}" style="margin-left: auto; flex-shrink: 0;">
								{event.severity}
							</span>
						</div>
					{/each}
					{#if recentEvents.length === 0}
						<p style="margin: 0; color: var(--color-on-surface-variant);">
							{isLoading ? 'Loading recent system events...' : 'No recent system events.'}
						</p>
					{/if}
				</div>
			{:else if activeSection === 'users'}
				<div class="animate-fade-up stagger-1" style="background: var(--color-surface-container-lowest); padding: 28px;">
					<p class="font-label" style="margin: 0 0 8px;">User Directory</p>
					<h2 class="font-headline-md" style="margin: 0;">Registered Accounts</h2>
					<p style="margin: 8px 0 0; color: var(--color-on-surface-variant); font-size: 0.8125rem;">
						Live user events from backend activity feed.
					</p>
				</div>

				<div class="applications-table animate-fade-up stagger-2">
					<table class="data-table">
						<thead>
							<tr>
								<th>Joined</th>
								<th>User</th>
								<th>Role</th>
								<th>Event</th>
							</tr>
						</thead>
						<tbody>
							{#each userEvents as event}
								<tr>
									<td>{formatEventDate(event.occurred_at)} {formatEventTime(event.occurred_at)}</td>
									<td style="font-weight: 600;">{event.actor}</td>
									<td>{event.message.includes('Admin') ? 'Admin' : 'Member'}</td>
									<td>{event.message}</td>
								</tr>
							{/each}
							{#if userEvents.length === 0}
								<tr>
									<td colspan="4" style="text-align: center; color: var(--color-on-surface-variant);">
										{isLoading ? 'Loading user events...' : 'No user events found.'}
									</td>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			{:else if activeSection === 'analytics'}
				<div class="kpi-grid animate-fade-up stagger-1">
					{#each [
						{ label: 'Total Deposits', value: 'UGX ' + (systemStats.totalDeposits / 1e6).toFixed(2) + 'M', icon: 'savings', note: `${systemStats.totalTransactions} total transactions` },
						{ label: 'Loan Book', value: 'UGX ' + (systemStats.loanBook / 1e6).toFixed(2) + 'M', icon: 'receipt_long', note: `${systemStats.activeLoans} active loans` },
						{ label: 'Notification Success', value: asPercent(notificationSuccessRatio()), icon: 'sms', note: `${systemStats.totalNotifications} processed` },
						{ label: 'Average Deposit/Tx', value: `UGX ${f(systemStats.totalTransactions > 0 ? systemStats.totalDeposits / systemStats.totalTransactions : 0)}`, icon: 'trending_up', note: 'Computed from live totals' },
					] as metric}
						<div class="kpi-card">
							<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
								<p class="stat-label" style="margin: 0;">{metric.label}</p>
								<span class="material-icons" style="font-size: 18px; color: var(--color-on-surface-variant);">{metric.icon}</span>
							</div>
							<p class="stat-value" style="margin: 0 0 8px; font-size: 1.75rem;">{metric.value}</p>
							<p style="margin: 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{metric.note}</p>
						</div>
					{/each}
				</div>

				<div class="animate-fade-up stagger-2" style="background: var(--color-surface-container-lowest); padding: 28px;">
					<p class="font-label" style="margin: 0 0 8px;">Transaction Activity</p>
					<p style="margin: 0; color: var(--color-on-surface-variant); font-size: 0.8125rem;">
						Recent transaction events: {transactionEvents.length} · Recent SMS events: {notificationEvents.length}
					</p>
				</div>
			{:else if activeSection === 'lending'}
				<div class="animate-fade-up stagger-1">
					<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
						<div>
							<p class="font-label" style="margin: 0 0 4px;">Lending Operations</p>
							<h2 class="font-headline-md" style="margin: 0;">Pending Decisions</h2>
						</div>
						<span class="badge">{pendingCount} Pending</span>
					</div>

					<div class="applications-table">
						<table class="data-table">
							<thead>
								<tr>
									<th>Application ID</th>
									<th>Applicant</th>
									<th>Loan Type</th>
									<th>Amount</th>
									<th>Submitted</th>
									<th>Status</th>
									<th>Actions</th>
								</tr>
							</thead>
							<tbody>
								{#each pendingApplications as app}
									{@const state =
										actionStates[String(app.applicationId)] ??
										(app.status === 'approved' ? 'approved' : app.status === 'rejected' ? 'rejected' : undefined)}
									<tr class:row-approved={state === 'approved'} class:row-rejected={state === 'rejected'}>
										<td style="font-weight: 700; font-size: 0.75rem; letter-spacing: 0.04em;">{app.id}</td>
										<td style="font-weight: 600;">{app.name}</td>
										<td style="color: var(--color-on-surface-variant);">{app.type}</td>
										<td style="font-weight: 700;">UGX {f(app.amount)}</td>
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
														onclick={() => handleAction(app.applicationId, 'approve')}
													>
														{state === 'approving' ? '...' : 'Approve'}
													</button>
													<button
														class="btn-secondary"
														style="padding: 8px 16px; font-size: 0.6rem; background: var(--color-error-container); color: var(--color-error);"
														disabled={state === 'approving' || state === 'rejecting'}
														onclick={() => handleAction(app.applicationId, 'reject')}
													>
														{state === 'rejecting' ? '...' : 'Reject'}
													</button>
												</div>
											{/if}
										</td>
									</tr>
								{/each}
								{#if pendingApplications.length === 0}
									<tr>
										<td colspan="7" style="text-align: center; color: var(--color-on-surface-variant);">
											{isLoading ? 'Loading lending queue...' : 'No pending loan applications.'}
										</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>

				<div class="animate-fade-up stagger-2" style="background: var(--color-surface-container-lowest); padding: 28px;">
					<p class="font-label" style="margin: 0 0 12px;">Recent Lending Events</p>
					{#each lendingEvents as event}
						<p style="margin: 0 0 8px; font-size: 0.8125rem;">
							<strong>{formatEventTime(event.occurred_at)}</strong> — {event.message}
						</p>
					{/each}
					{#if lendingEvents.length === 0}
						<p style="margin: 0; color: var(--color-on-surface-variant);">
							{isLoading ? 'Loading lending events...' : 'No lending events available.'}
						</p>
					{/if}
				</div>
			{:else if activeSection === 'audit'}
				<div class="applications-table animate-fade-up stagger-1">
					<table class="data-table">
						<thead>
							<tr>
								<th>Timestamp</th>
								<th>Type</th>
								<th>Message</th>
								<th>Actor</th>
								<th>Severity</th>
							</tr>
						</thead>
						<tbody>
							{#each recentEvents as event}
								<tr>
									<td>{formatEventDate(event.occurred_at)} {formatEventTime(event.occurred_at)}</td>
									<td style="font-family: monospace;">{event.event_type}</td>
									<td>{event.message}</td>
									<td>{event.actor}</td>
									<td><span class="badge">{event.severity}</span></td>
								</tr>
							{/each}
							{#if recentEvents.length === 0}
								<tr>
									<td colspan="5" style="text-align: center; color: var(--color-on-surface-variant);">
										{isLoading ? 'Loading audit events...' : 'No audit events found.'}
									</td>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			{:else}
				<div class="kpi-grid animate-fade-up stagger-1">
					{#each [
						{ label: 'Auth Mode', value: 'Token', icon: 'verified_user', note: 'Backend DRF token authentication' },
						{ label: 'Base Currency', value: 'UGX', icon: 'payments', note: 'Unified Uganda Shillings display' },
						{ label: 'SMS Provider', value: 'Africa\'s Talking', icon: 'sms', note: `${systemStats.totalNotifications} notifications recorded` },
						{ label: 'Config Health', value: loadError ? 'Attention' : 'Healthy', icon: 'tune', note: loadError ? loadError : 'No configuration errors detected' },
					] as setting}
						<div class="kpi-card">
							<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
								<p class="stat-label" style="margin: 0;">{setting.label}</p>
								<span class="material-icons" style="font-size: 18px; color: var(--color-on-surface-variant);">{setting.icon}</span>
							</div>
							<p class="stat-value" style="margin: 0 0 8px; font-size: 1.25rem;">{setting.value}</p>
							<p style="margin: 0; font-size: 0.6875rem; color: var(--color-on-surface-variant);">{setting.note}</p>
						</div>
					{/each}
				</div>

				<div class="animate-fade-up stagger-2" style="display: flex; gap: 12px;">
					<button type="button" class="btn-primary" onclick={() => void loadAdminData()}>
						<span class="material-icons" style="font-size: 14px;">refresh</span>
						Refresh Runtime Data
					</button>
				</div>
			{/if}
		</div>

		<footer class="footer" style="background: var(--color-surface-container);">
			<p class="font-label" style="margin: 0;">© 2026 G VAULT — ADMIN TERMINAL</p>
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
