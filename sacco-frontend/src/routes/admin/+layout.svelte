<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getStoredToken, getStoredUser } from '$lib/auth/session';

	let { children } = $props();
	let authorized = $state(false);

	onMount(() => {
		const token = getStoredToken();
		const user = getStoredUser();

		if (!token) {
			goto('/');
		} else if (!user?.is_staff) {
			// Non-admin users get redirected to the member dashboard
			goto('/dashboard');
		} else {
			authorized = true;
		}
	});
</script>

{#if authorized}
	{@render children()}
{:else}
	<div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--color-surface);">
		<p style="color: var(--color-on-surface-variant); font-size: 0.875rem;">Verifying admin credentials...</p>
	</div>
{/if}
