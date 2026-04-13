<script lang="ts">
	let { active = 'overview', onchange } = $props<{
		active?: string;
		onchange?: (section: string) => void;
	}>();

	const navItems = [
		{ id: 'overview', label: 'Overview', icon: 'dashboard' },
		{ id: 'users', label: 'Users', icon: 'group' },
		{ id: 'analytics', label: 'Analytics', icon: 'monitoring' },
		{ id: 'lending', label: 'Lending', icon: 'account_balance' },
		{ id: 'audit', label: 'Audit', icon: 'receipt_long' },
		{ id: 'settings', label: 'Settings', icon: 'tune' },
	];
</script>

<aside class="sidebar">
	<div class="sidebar-brand">
		<span style="font-size: 0.5rem; color: var(--color-on-surface-variant); display: block; margin-bottom: 4px; letter-spacing: 0.12em;">G VAULT</span>
		<span style="font-size: 0.875rem; font-weight: 800; letter-spacing: 0.06em; color: var(--color-on-surface);">ADMIN TERMINAL</span>
	</div>

	<nav class="sidebar-nav">
		{#each navItems as item}
			<button
				class="sidebar-link"
				class:active={active === item.id}
				onclick={() => onchange?.(item.id)}
				id="admin-nav-{item.id}"
				style="width: 100%; text-align: left; background: none; border: none; cursor: pointer;"
			>
				<span class="material-icons">{item.icon}</span>
				{item.label}
			</button>
		{/each}
	</nav>

	<!-- Bottom nav items for member portal -->
	<div style="padding: 16px 0; border-top: none;">
		<p class="font-label" style="padding: 0 24px; margin: 0 0 8px; color: var(--color-on-surface-variant); opacity: 0.6;">Portal Links</p>
		<a href="/dashboard" class="sidebar-link" style="font-size: 0.6875rem;">
			<span class="material-icons">person</span>
			Dashboard
		</a>
		<a href="/dashboard/accounts" class="sidebar-link" style="font-size: 0.6875rem;">
			<span class="material-icons">account_balance</span>
			Accounts
		</a>
		<a href="/dashboard/loans" class="sidebar-link" style="font-size: 0.6875rem;">
			<span class="material-icons">receipt_long</span>
			Loans
		</a>
	</div>

	<div style="padding: 24px; margin-top: auto;">
		<a href="/" class="btn-ghost" style="font-size: 0.625rem; width: 100%;">
			<span class="material-icons" style="font-size: 15px;">logout</span>
			Sign Out
		</a>
	</div>
</aside>
