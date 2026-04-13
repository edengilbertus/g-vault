<script lang="ts">
	import MemberNav from '$lib/components/MemberNav.svelte';

	let subject = $state('');
	let message = $state('');
	let isSubmitting = $state(false);
	let submitted = $state(false);

	const tickets = [
		{ id: 'TKT-9281', subject: 'Card delivery status', status: 'Resolved', date: 'Apr 02' },
		{ id: 'TKT-8452', subject: 'Disputed transaction at Apple Store', status: 'In Review', date: 'Apr 14' },
	];

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		isSubmitting = true;
		await new Promise((r) => setTimeout(r, 1200));
		isSubmitting = false;
		submitted = true;
	}
</script>

<svelte:head>
	<title>G Vault | Support</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="support" />

	<div class="main-content">
		<div class="dashboard-body">
			<div class="section-header animate-fade-up stagger-1">
				<h1 class="font-display" style="margin: 0;">CLIENT<br />SUPPORT</h1>
				<p style="color: var(--color-on-surface-variant); max-width: 400px; text-align: right; font-size: 0.875rem; line-height: 1.6;">
					Priority access for Premium Members. Our concierge team normally responds within 2 hours during business operations.
				</p>
			</div>

			<div class="support-grid animate-fade-up stagger-2" style="margin-top: 48px;">
				<!-- Contact Form -->
				<div>
					<p class="font-label" style="margin: 0 0 24px;">New Request</p>
					
					{#if submitted}
						<div style="background: var(--color-surface-container-low); padding: 32px; text-align: center;">
							<span class="material-icons" style="font-size: 32px; color: #1a7f37; margin-bottom: 16px;">check_circle</span>
							<h3 style="margin: 0 0 8px; font-size: 1.25rem;">Request Received</h3>
							<p style="margin: 0 0 24px; font-size: 0.875rem; color: var(--color-on-surface-variant);">Ticket TKT-{Math.floor(Math.random() * 9000)+1000} has been created.</p>
							<button class="btn-ghost" onclick={() => { submitted = false; subject = ''; message = ''; }}>Open another ticket</button>
						</div>
					{:else}
						<form onsubmit={handleSubmit} style="background: var(--color-surface-container-lowest); padding: 32px; border: 1px solid var(--color-surface-container-high);">
							<div class="input-group" style="margin-bottom: 24px;">
								<label for="subject" class="input-label">Subject</label>
								<select id="subject" class="select-field" bind:value={subject} required>
									<option value="">Select category...</option>
									<option value="account">Account Query</option>
									<option value="card">Card Services</option>
									<option value="transaction">Disputed Transaction</option>
									<option value="loan">Loan Assistance</option>
									<option value="other">Other Inquiry</option>
								</select>
							</div>

							<div class="input-group" style="margin-bottom: 32px;">
								<label for="message" class="input-label">Message</label>
								<textarea id="message" class="input-field" rows="6" placeholder="Describe your issue..." bind:value={message} required></textarea>
							</div>

							<button type="submit" class="btn-primary" style="width: 100%; justify-content: center;" disabled={isSubmitting}>
								{#if isSubmitting}
									<span class="material-icons spin" style="font-size: 16px;">autorenew</span>
									Sending...
								{:else}
									Submit Request
								{/if}
							</button>
						</form>
					{/if}
				</div>

				<!-- Active Tickets & Contact Info -->
				<div>
					<p class="font-label" style="margin: 0 0 24px;">Active Tickets</p>
					
					<div style="display: flex; flex-direction: column; gap: 16px;">
						{#each tickets as ticket}
							<div style="background: var(--color-surface-container-lowest); border: 1px solid var(--color-surface-container-high); padding: 20px;">
								<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
									<span style="font-size: 0.6875rem; font-family: monospace; color: var(--color-on-surface-variant);">{ticket.id}</span>
									<span class="badge {ticket.status === 'Resolved' ? 'badge-success' : 'badge-pending'}">{ticket.status}</span>
								</div>
								<p style="margin: 0 0 12px; font-weight: 600; font-size: 0.875rem;">{ticket.subject}</p>
								<p style="margin: 0; font-size: 0.75rem; color: var(--color-on-surface-variant);">Updated {ticket.date}</p>
							</div>
						{/each}
					</div>

					<div style="margin-top: 48px;">
						<p class="font-label" style="margin: 0 0 24px;">Direct Contact</p>
						<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
							<div>
								<p style="margin: 0 0 4px; font-weight: 600; font-size: 0.875rem;">Global Concierge</p>
								<p style="margin: 0; font-family: monospace; font-size: 0.875rem; color: var(--color-on-surface-variant);">+256 (200) 555-0199</p>
							</div>
							<div>
								<p style="margin: 0 0 4px; font-weight: 600; font-size: 0.875rem;">Email</p>
								<p style="margin: 0; font-family: monospace; font-size: 0.875rem; color: var(--color-on-surface-variant);">support@gvault.com</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Footer -->
		<footer class="footer">
			<p class="font-label" style="margin: 0;">© 2026 G VAULT</p>
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
	.page-wrap {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background-color: var(--color-surface);
	}

	.dashboard-body {
		padding: 56px 40px;
		display: flex;
		flex-direction: column;
		flex: 1;
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
	}

	.support-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 64px;
	}

	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}
	@keyframes spin {
		from { transform: rotate(0deg); }
		to   { transform: rotate(360deg); }
	}

	@media (max-width: 1024px) {
		.support-grid { gap: 40px; }
	}

	@media (max-width: 768px) {
		.dashboard-body { padding: 32px 20px; }
		.section-header { flex-direction: column; align-items: flex-start; gap: 24px; }
		.section-header p { text-align: left; }
		.support-grid { grid-template-columns: 1fr; gap: 48px; }
	}
</style>
