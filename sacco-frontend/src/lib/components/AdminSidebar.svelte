<script lang="ts">
	import { goto } from '$app/navigation';
	import { logout } from '$lib/api/client';
	import { clearSession, getStoredToken } from '$lib/auth/session';

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

	async function handleSignOut() {
		const token = getStoredToken();
		try {
			if (token) {
				await logout(token);
			}
		} catch {
			// Best-effort logout: clear local session regardless of API response.
		} finally {
			clearSession();
			goto('/');
		}
	}
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

	<div style="padding: 24px; margin-top: auto;">
		<button type="button" onclick={handleSignOut} class="btn-ghost" style="font-size: 0.625rem; width: 100%;">
			<span class="material-icons" style="font-size: 15px;">logout</span>
			Sign Out
		</button>
	</div>
</aside>
