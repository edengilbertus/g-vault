<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { getStoredToken } from '$lib/auth/session';

	let { children } = $props();
	let authorized = $state(false);

	onMount(() => {
		if (!getStoredToken()) {
			goto('/');
		} else {
			authorized = true;
		}
	});
</script>

{#if authorized}
	{@render children()}
{:else}
	<div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--color-surface);">
		<p style="color: var(--color-on-surface-variant); font-size: 0.875rem;">Authenticating...</p>
	</div>
{/if}
