<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>G Vault</title>
	<meta name="description" content="G Vault — Architectural precision in every transaction." />
</svelte:head>

{@render children()}
