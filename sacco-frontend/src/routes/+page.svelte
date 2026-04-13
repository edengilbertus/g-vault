<script lang="ts">
	import { goto } from '$app/navigation';

	let activeTab = $state<'login' | 'register'>('login');
	let showPassword = $state(false);
	let isLoading = $state(false);

	// Login form
	let loginEmail = $state('');
	let loginPassword = $state('');

	// Register form
	let regName = $state('');
	let regEmail = $state('');
	let regPassword = $state('');
	let regConfirm = $state('');
	let regPhone = $state('');

	let errorMsg = $state('');

	async function handleLogin(e: SubmitEvent) {
		e.preventDefault();
		errorMsg = '';
		isLoading = true;
		await new Promise((r) => setTimeout(r, 800));
		isLoading = false;
		// Simulate role routing
		if (loginEmail.includes('admin')) {
			goto('/admin');
		} else {
			goto('/dashboard');
		}
	}

	async function handleRegister(e: SubmitEvent) {
		e.preventDefault();
		errorMsg = '';
		if (regPassword !== regConfirm) {
			errorMsg = 'Passwords do not match.';
			return;
		}
		isLoading = true;
		await new Promise((r) => setTimeout(r, 800));
		isLoading = false;
		goto('/dashboard');
	}
</script>

<svelte:head>
	<title>G Vault — Secure Access</title>
</svelte:head>

<div class="auth-root">
	<!-- Left panel: Brand Statement -->
	<aside class="auth-brand animate-fade-up stagger-1">
		<div class="auth-brand-inner">
			<p class="font-label" style="color: var(--color-on-surface-variant); margin-bottom: 40px;">
				EST. 2024
			</p>
			<h1 class="font-display" style="color: var(--color-on-primary-container); margin: 0 0 24px;">
				G<br />VAULT
			</h1>
			<p class="auth-tagline">
				Architectural precision<br />in every transaction.
			</p>
			<div class="auth-brand-meta">
				<span class="font-label" style="color: rgba(255,255,255,0.4);">FDIC INSURED</span>
				<span class="font-label" style="color: rgba(255,255,255,0.4);">SSL 256-BIT</span>
				<span class="font-label" style="color: rgba(255,255,255,0.4);">ISO 27001</span>
			</div>
		</div>
	</aside>

	<!-- Right panel: Form -->
	<main class="auth-form-panel">
		<div class="auth-form-inner animate-fade-up stagger-2">
			<!-- Tab selector -->
			<div class="auth-tabs">
				<button
					class="auth-tab"
					class:auth-tab-active={activeTab === 'login'}
					onclick={() => { activeTab = 'login'; errorMsg = ''; }}
				>
					Sign In
				</button>
				<button
					class="auth-tab"
					class:auth-tab-active={activeTab === 'register'}
					onclick={() => { activeTab = 'register'; errorMsg = ''; }}
				>
					Create Account
				</button>
			</div>

			{#if activeTab === 'login'}
				<form onsubmit={handleLogin} class="auth-fields animate-fade-up">
					<div class="input-group">
						<label for="login-email" class="input-label">Email Address</label>
						<input
							id="login-email"
							type="email"
							class="input-field"
							placeholder="you@example.com"
							bind:value={loginEmail}
							required
							autocomplete="email"
						/>
					</div>

					<div class="input-group" style="margin-top: 20px;">
						<label for="login-password" class="input-label">Password</label>
						<div style="position: relative;">
							<input
								id="login-password"
								type={showPassword ? 'text' : 'password'}
								class="input-field"
								placeholder="••••••••"
								bind:value={loginPassword}
								required
								autocomplete="current-password"
								style="padding-right: 48px;"
							/>
							<button
								type="button"
								onclick={() => (showPassword = !showPassword)}
								class="pw-toggle"
								aria-label="Toggle password visibility"
							>
								<span class="material-icons" style="font-size: 18px; color: var(--color-on-surface-variant);">
									{showPassword ? 'visibility_off' : 'visibility'}
								</span>
							</button>
						</div>
					</div>

					{#if errorMsg}
						<p class="auth-error animate-fade-in">{errorMsg}</p>
					{/if}

					<div style="display: flex; justify-content: flex-end; margin-top: 12px;">
						<a href="/forgot-password" class="btn-ghost" style="font-size: 0.6875rem;">Forgot password?</a>
					</div>

					<button type="submit" class="btn-primary" style="width: 100%; margin-top: 32px; justify-content: center;" disabled={isLoading}>
						{#if isLoading}
							<span class="material-icons spin" style="font-size: 16px;">autorenew</span>
							Authenticating...
						{:else}
							<span class="material-icons" style="font-size: 16px;">arrow_forward</span>
							Access Account
						{/if}
					</button>
				</form>

			{:else}
				<form onsubmit={handleRegister} class="auth-fields animate-fade-up">
					<div class="input-group">
						<label for="reg-name" class="input-label">Full Legal Name</label>
						<input
							id="reg-name"
							type="text"
							class="input-field"
							placeholder="Julian Thorne"
							bind:value={regName}
							required
						/>
					</div>

					<div class="input-group" style="margin-top: 20px;">
						<label for="reg-email" class="input-label">Email Address</label>
						<input
							id="reg-email"
							type="email"
							class="input-field"
							placeholder="you@example.com"
							bind:value={regEmail}
							required
						/>
					</div>

					<div class="input-group" style="margin-top: 20px;">
						<label for="reg-phone" class="input-label">Phone Number</label>
						<input
							id="reg-phone"
							type="tel"
							class="input-field"
							placeholder="+256 700 000 000"
							bind:value={regPhone}
							required
						/>
					</div>

					<div class="input-group" style="margin-top: 20px;">
						<label for="reg-password" class="input-label">Create Password</label>
						<input
							id="reg-password"
							type="password"
							class="input-field"
							placeholder="Minimum 8 characters"
							bind:value={regPassword}
							required
							minlength="8"
						/>
					</div>

					<div class="input-group" style="margin-top: 20px;">
						<label for="reg-confirm" class="input-label">Confirm Password</label>
						<input
							id="reg-confirm"
							type="password"
							class="input-field"
							placeholder="Repeat password"
							bind:value={regConfirm}
							required
						/>
					</div>

					{#if errorMsg}
						<p class="auth-error animate-fade-in">{errorMsg}</p>
					{/if}

					<button type="submit" class="btn-primary" style="width: 100%; margin-top: 32px; justify-content: center;" disabled={isLoading}>
						{#if isLoading}
							<span class="material-icons spin" style="font-size: 16px;">autorenew</span>
							Processing...
						{:else}
							<span class="material-icons" style="font-size: 16px;">arrow_forward</span>
							Create Account
						{/if}
					</button>
				</form>
			{/if}

			<!-- Footer links -->
			<div class="auth-footer-links">
				<a href="/legal/privacy" class="footer-link">Privacy</a>
				<a href="/legal/terms" class="footer-link">Terms</a>
				<a href="/legal/security" class="footer-link">Security</a>
				<a href="/legal/accessibility" class="footer-link">Accessibility</a>
			</div>
		</div>
	</main>
</div>

<style>
	.auth-root {
		display: flex;
		min-height: 100vh;
	}

	/* ── Left Brand Panel ── */
	.auth-brand {
		width: 40%;
		background-color: var(--color-primary);
		display: flex;
		align-items: flex-start;
		justify-content: flex-start;
		flex-direction: column;
		padding: 80px 56px;
		position: relative;
		overflow: hidden;
	}

	.auth-brand::after {
		content: 'M';
		position: absolute;
		bottom: -60px;
		right: -30px;
		font-size: 320px;
		font-weight: 900;
		color: rgba(255, 255, 255, 0.04);
		line-height: 1;
		letter-spacing: -0.05em;
		pointer-events: none;
		user-select: none;
	}

	.auth-brand-inner {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.auth-tagline {
		font-size: 1rem;
		font-weight: 300;
		line-height: 1.7;
		color: rgba(255, 255, 255, 0.5);
		margin: 0;
	}

	.auth-brand-meta {
		margin-top: auto;
		display: flex;
		gap: 24px;
	}

	/* ── Right Form Panel ── */
	.auth-form-panel {
		flex: 1;
		background-color: var(--color-surface);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 80px 40px;
	}

	.auth-form-inner {
		width: 100%;
		max-width: 400px;
	}

	/* ── Auth Tabs ── */
	.auth-tabs {
		display: flex;
		gap: 0;
		margin-bottom: 48px;
	}

	.auth-tab {
		flex: 1;
		padding: 12px 0;
		font-family: var(--font-family);
		font-size: 0.6875rem;
		font-weight: 700;
		letter-spacing: var(--tracking-xwide);
		text-transform: uppercase;
		color: var(--color-on-surface-variant);
		background: none;
		border: none;
		border-bottom: 2px solid var(--color-outline-variant);
		cursor: pointer;
		transition: color 0.15s, border-color 0.15s;
	}

	.auth-tab:hover {
		color: var(--color-on-surface);
	}

	.auth-tab-active {
		color: var(--color-on-surface);
		border-bottom-color: var(--color-primary);
	}

	/* ── Fields Container ── */
	.auth-fields {
		display: flex;
		flex-direction: column;
	}

	/* ── Error ── */
	.auth-error {
		font-size: 0.75rem;
		color: var(--color-error);
		margin: 12px 0 0;
		font-weight: 500;
		letter-spacing: 0.01em;
	}

	/* ── Password toggle button ── */
	.pw-toggle {
		position: absolute;
		right: 12px;
		top: 50%;
		transform: translateY(-50%);
		background: none;
		border: none;
		cursor: pointer;
		padding: 4px;
		display: flex;
		align-items: center;
	}

	/* ── Footer links ── */
	.auth-footer-links {
		display: flex;
		gap: 20px;
		margin-top: 48px;
		flex-wrap: wrap;
	}

	/* ── Spin animation ── */
	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to   { transform: rotate(360deg); }
	}

	@media (max-width: 768px) {
		.auth-root { flex-direction: column; }
		.auth-brand {
			width: 100%;
			min-height: 200px;
			padding: 48px 32px;
		}
		.auth-brand::after { display: none; }
		.auth-brand-meta { margin-top: 32px; }
	}
</style>
