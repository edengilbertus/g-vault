<script lang="ts">
	import { page } from '$app/state';

	let { active = 'dashboard' } = $props<{ active?: string }>();

	const links = [
		{ href: '/dashboard', label: 'Dashboard', icon: 'dashboard', id: 'dashboard' },
		{ href: '/dashboard/accounts', label: 'Accounts', icon: 'account_balance', id: 'accounts' },
		{ href: '/dashboard/loans', label: 'Loans', icon: 'receipt_long', id: 'loans' },
		{ href: '/dashboard/transfer', label: 'Transfer', icon: 'swap_horiz', id: 'transfer' },
		{ href: '/dashboard/support', label: 'Support', icon: 'support_agent', id: 'support' },
	];
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
			<div class="member-avatar">JT</div>
			<div>
				<p class="member-name">Julian Thorne</p>
				<p class="member-tier">Premium Member</p>
			</div>
		</div>
		<a href="/" class="btn-ghost" aria-label="Sign out">
			<span class="material-icons" style="font-size: 18px;">logout</span>
		</a>
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
