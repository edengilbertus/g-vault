<script lang="ts">
	let email = $state('');
	let isSubmitting = $state(false);
	let submitted = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		isSubmitting = true;
		await new Promise(r => setTimeout(r, 1200));
		isSubmitting = false;
		submitted = true;
	}
</script>

<svelte:head>
	<title>G Vault | Recover Account</title>
</svelte:head>

<div class="auth-layout">
	<!-- Left Panel (Form) -->
	<div class="auth-panel">
		<header class="auth-header">
			<a href="/" class="brand-logo font-display">G VAULT.</a>
		</header>

		<div class="auth-content">
			<div class="animate-fade-up">
				{#if submitted}
					<span class="material-icons" style="font-size: 40px; color: var(--color-on-surface); margin-bottom: 24px;">mail_outline</span>
					<h1 class="font-display" style="margin: 0 0 16px;">CHECK YOUR<br />INBOX</h1>
					<p style="color: var(--color-on-surface-variant); line-height: 1.6; margin: 0 0 32px;">
						If an account exists for <strong>{email}</strong>, we have sent instructions to reset your password.
					</p>
					<a href="/login" class="btn-primary" style="width: 100%; justify-content: center;">Return to Sign In</a>
				{:else}
					<h1 class="font-display" style="margin: 0 0 16px;">ACCOUNT<br />RECOVERY</h1>
					<p style="color: var(--color-on-surface-variant); line-height: 1.6; margin: 0 0 40px;">
						Enter the email address associated with your account. We will transmit a secure recovery link.
					</p>

					<form onsubmit={handleSubmit}>
						<div class="input-group" style="margin-bottom: 32px;">
							<label for="email" class="input-label">Email Address</label>
							<input id="email" type="email" class="input-field" placeholder="identifier@domain.com" bind:value={email} required />
						</div>

						<button type="submit" class="btn-primary" style="width: 100%; justify-content: center; margin-bottom: 24px;" disabled={isSubmitting}>
							{#if isSubmitting}
								<span class="material-icons spin" style="font-size: 16px;">autorenew</span> Transmitting...
							{:else}
								Send Recovery Link <span class="material-icons" style="font-size: 16px;">arrow_forward</span>
							{/if}
						</button>

						<div style="text-align: center;">
							<a href="/login" class="auth-link font-label">Return to Sign In</a>
						</div>
					</form>
				{/if}
			</div>
		</div>

		<footer class="footer">
			<p class="font-label" style="margin: 0;">© 2024 G VAULT</p>
			<div class="footer-links">
				<a href="/legal/privacy" class="footer-link">Privacy</a>
				<a href="/legal/terms" class="footer-link">Terms</a>
			</div>
		</footer>
	</div>

	<!-- Right Panel (Imagery/Branding) -->
	<div class="auth-brand">
		<div class="brand-content animate-fade-up stagger-1">
			<h2 class="font-display" style="margin: 0 0 24px;">SECURE.<br />ENCRYPTED.<br />G VAULT.</h2>
			<p class="font-label" style="color: var(--color-on-surface-variant); max-width: 300px; line-height: 1.6;">
				ACCOUNT SECURITY PROTOCOLS ARE ENFORCED.
			</p>
		</div>
	</div>
</div>

<style>
	.auth-layout {
		display: flex;
		min-height: 100vh;
		background: var(--color-surface);
	}

	.auth-panel {
		flex: 1;
		display: flex;
		flex-direction: column;
		max-width: 600px;
		background: var(--color-surface-container-lowest);
	}

	.auth-header {
		padding: 32px 40px;
	}

	.brand-logo {
		font-size: 1.125rem;
		font-weight: 800;
		color: var(--color-on-surface);
		text-decoration: none;
		letter-spacing: 0.05em;
	}

	.auth-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 40px 64px;
	}

	.auth-link {
		color: var(--color-on-surface-variant);
		text-decoration: none;
		font-size: 0.75rem;
		transition: color 0.15s ease;
	}

	.auth-link:hover {
		color: var(--color-on-surface);
		text-decoration: underline;
	}

	.auth-brand {
		flex: 1.2;
		background: var(--color-surface-container-high);
		display: flex;
		align-items: center;
		padding: 80px;
		border-left: 1px solid var(--color-surface-container-highest);
	}

	.brand-content h2 {
		font-size: 4vw;
		line-height: 1.1;
		letter-spacing: -0.02em;
	}

	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}
	@keyframes spin {
		from { transform: rotate(0deg); }
		to   { transform: rotate(360deg); }
	}

	@media (max-width: 1024px) {
		.auth-brand { display: none; }
		.auth-panel { max-width: 100%; border-right: none; }
		.auth-content { padding: 40px 32px; }
	}
</style>
