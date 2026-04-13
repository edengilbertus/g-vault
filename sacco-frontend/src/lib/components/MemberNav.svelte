<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { logout, me } from '$lib/api/client';
	import { clearSession, getStoredToken, getStoredUser, persistSession } from '$lib/auth/session';

	let { active = 'dashboard' } = $props<{ active?: string }>();

	const links = [
		{ href: '/dashboard', label: 'Dashboard', icon: 'dashboard', id: 'dashboard' },
		{ href: '/dashboard/accounts', label: 'Accounts', icon: 'account_balance', id: 'accounts' },
		{ href: '/dashboard/loans', label: 'Loans', icon: 'receipt_long', id: 'loans' },
		{ href: '/dashboard/transfer', label: 'Transfer', icon: 'swap_horiz', id: 'transfer' },
		{ href: '/dashboard/statement', label: 'Statement', icon: 'receipt', id: 'statement' },
		{ href: '/dashboard/support', label: 'Support', icon: 'support_agent', id: 'support' },
		{ href: '/dashboard/profile', label: 'Profile', icon: 'person', id: 'profile' },
		{ href: '/dashboard/withdrawal', label: 'Withdraw', icon: 'payments', id: 'withdrawal' },
	];

	let memberName = $state('Member');
	let memberTier = $state('Member');
	let memberInitials = $state('GV');

	function getInitials(name: string): string {
		const parts = name.trim().split(/\s+/);
		if (parts.length === 0 || !parts[0]) return 'GV';
		if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
		return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
	}

	const storedUser = getStoredUser();
	if (storedUser) {
		memberName = storedUser.full_name;
		memberTier = storedUser.is_staff ? 'Administrator' : 'Member';
		memberInitials = getInitials(storedUser.full_name);
	}

	onMount(() => {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		void me(token)
			.then((user) => {
				persistSession(token, user);
				memberName = user.full_name;
				memberTier = user.is_staff ? 'Administrator' : 'Member';
				memberInitials = getInitials(user.full_name);
				if (user.is_staff) {
					goto('/admin');
				}
			})
			.catch(() => {
				clearSession();
				goto('/');
			});
	});

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

<nav class="nav" style="position: sticky; top: 0; z-index: 100;">
	<a href="/dashboard" class="nav-brand">G VAULT</a>

	<ul class="nav-links">
		{#each links as link}
			<li>
				<a
					href={link.href}
					class="nav-link"
					class:active={active === link.id}
					id="nav-{link.id}"
				>
					{link.label}
				</a>
			</li>
		{/each}
	</ul>

	<div style="display: flex; align-items: center; gap: 20px;">
		<div class="member-badge">
			<div class="member-avatar">{memberInitials}</div>
			<div>
				<p class="member-name">{memberName}</p>
				<p class="member-tier">{memberTier}</p>
			</div>
		</div>
		<button type="button" class="btn-ghost" aria-label="Sign out" onclick={handleSignOut}>
			<span class="material-icons" style="font-size: 18px;">logout</span>
		</button>
	</div>
</nav>

<style>
	.member-badge {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.member-avatar {
		width: 36px;
		height: 36px;
		background: var(--color-primary);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.625rem;
		font-weight: 800;
		letter-spacing: 0.05em;
		flex-shrink: 0;
	}

	.member-name {
		margin: 0;
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-on-surface);
	}

	.member-tier {
		margin: 0;
		font-size: 0.625rem;
		font-weight: 500;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--color-on-surface-variant);
	}

	@media (max-width: 768px) {
		.member-badge { display: none; }
	}
</style>
