<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { createTransfer, fetchDashboardSummary } from '$lib/api/client';
	import { getStoredToken } from '$lib/auth/session';
	import MemberNav from '$lib/components/MemberNav.svelte';

	let transferType = $state('internal'); // 'internal' or 'external'
	let fromAccount = $state('');
	let toAccount = $state('');
	let amount = $state('');
	let note = $state('');

	let isSubmitting = $state(false);
	let isLoadingBalance = $state(true);
	let submitted = $state(false);
	let errorMsg = $state('');
	let referenceId = $state('');
	let availableBalance = $state(0);

	function formatMoney(n: number) {
		return `UGX ${Math.round(n).toLocaleString('en-UG')}`;
	}

	async function loadBalance() {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		isLoadingBalance = true;
		try {
			const summary = await fetchDashboardSummary(token);
			availableBalance = Number(summary.savings_balance);
			if (!fromAccount) {
				fromAccount = 'ACC-001';
			}
		} catch (error) {
			errorMsg = error instanceof Error ? error.message : 'Unable to load account balance.';
		} finally {
			isLoadingBalance = false;
		}
	}

	async function handleTransfer(e: SubmitEvent) {
		e.preventDefault();
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}
		const transferAmount = Number(amount);
		const destination = toAccount.trim();

		if (!transferAmount || transferAmount <= 0) {
			errorMsg = 'Enter a valid transfer amount.';
			return;
		}
		if (transferAmount > availableBalance) {
			errorMsg = 'Insufficient balance for transfer.';
			return;
		}
		if (!destination) {
			errorMsg = 'Destination account is required.';
			return;
		}

		errorMsg = '';
		isSubmitting = true;
		try {
			const response = await createTransfer(token, {
				transfer_type: transferType as 'internal' | 'external',
				destination,
				amount: transferAmount,
				note: note.trim() || undefined
			});
			referenceId = response.transaction.reference;
			availableBalance = Number(response.new_balance);

			submitted = true;
		} catch (error) {
			errorMsg = error instanceof Error ? error.message : 'Transfer failed.';
		} finally {
			isSubmitting = false;
		}
	}

	onMount(() => {
		void loadBalance();
	});
</script>

<svelte:head>
	<title>G Vault | Transfer</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="transfer" />

	<div class="main-content">
		<div class="loan-body">

			{#if submitted}
				<div class="submitted-state animate-fade-up">
					<span class="material-icons" style="font-size: 48px; color: #1a7f37; margin-bottom: 24px; display: block;">check_circle_outline</span>
					<h1 class="font-headline-lg" style="margin: 0 0 16px;">Transfer Initiated</h1>
					<p style="color: var(--color-on-surface-variant); margin: 0 0 32px; font-size: 0.9375rem; line-height: 1.6;">
						Your transfer of <strong>UGX {Number(amount).toLocaleString('en-UG')}</strong> has been successfully scheduled.
					</p>
					<p class="font-label" style="margin: 0 0 8px;">Reference ID</p>
					<p style="font-size: 1.5rem; font-weight: 800; letter-spacing: 0.08em; margin: 0 0 40px; font-family: monospace;">{referenceId}</p>
					
					<div style="display: flex; gap: 16px; justify-content: center;">
						<button class="btn-secondary" onclick={() => { submitted = false; amount = ''; note = ''; }}>New Transfer</button>
						<a href="/dashboard" class="btn-primary">Return to Dashboard</a>
					</div>
				</div>
			{:else}
				<div class="loan-header animate-fade-up stagger-1">
					<div>
						<p class="font-label" style="margin: 0 0 8px; color: var(--color-on-surface-variant);">Funds Management</p>
						<h1 class="font-display" style="margin: 0;">TRANSFER<br />CAPITAL</h1>
					</div>
				</div>

				<form onsubmit={handleTransfer} class="loan-form animate-fade-up stagger-2" style="max-width: 540px;">
					<!-- Transfer Type Toggle -->
					<div style="display: flex; gap: 2px; margin-bottom: 32px; background: var(--color-surface-container-low); padding: 4px;">
						<button 
							type="button"
							class="transfer-tab {transferType === 'internal' ? 'active' : ''}" 
							onclick={() => transferType = 'internal'}
						>
							Internal Transfer
						</button>
						<button 
							type="button"
							class="transfer-tab {transferType === 'external' ? 'active' : ''}" 
							onclick={() => transferType = 'external'}
						>
							Peer-to-Peer
						</button>
					</div>

					<div class="form-grid">
						<div class="input-group" style="grid-column: 1 / -1;">
							<label for="from-acc" class="input-label">From Account</label>
							<select id="from-acc" class="select-field" bind:value={fromAccount} required disabled={isLoadingBalance}>
								<option value="">Select source account...</option>
								<option value="ACC-001">Main Savings ({formatMoney(availableBalance)})</option>
							</select>
						</div>

						{#if transferType === 'internal'}
							<div class="input-group" style="grid-column: 1 / -1;">
								<label for="to-acc" class="input-label">To Account</label>
								<select id="to-acc" class="select-field" bind:value={toAccount} required>
									<option value="">Select destination account...</option>
									<option value="ACC-002">Emergency Fund</option>
									<option value="ACC-001">Main Savings</option>
									<option value="LN-001">Loan Repayment (LN-2026)</option>
								</select>
							</div>
						{:else}
							<div class="input-group" style="grid-column: 1 / -1;">
								<label for="to-member" class="input-label">Destination Member ID / Email</label>
								<input id="to-member" type="text" class="input-field" placeholder="e.g. mb_73829 or user@email.com" bind:value={toAccount} required />
							</div>
						{/if}

						<div class="input-group" style="grid-column: 1 / -1;">
							<label for="amount" class="input-label">Amount (UGX)</label>
							<input
								id="amount"
								type="number"
								class="input-field"
								placeholder="0"
								bind:value={amount}
								min="1"
								step="1"
								max={availableBalance > 0 ? String(Math.floor(availableBalance)) : undefined}
								required
								style="font-size: 1.5rem; padding: 16px;"
							/>
							<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0;">
								{isLoadingBalance ? 'Loading available balance...' : `Available Balance: ${formatMoney(availableBalance)}`}
							</p>
						</div>

						<div class="input-group" style="grid-column: 1 / -1;">
							<label for="note" class="input-label">Transfer Reference (Optional)</label>
							<input id="note" type="text" class="input-field" placeholder="e.g. Project funding" bind:value={note} />
						</div>
					</div>

					<div style="margin-top: 40px; padding-top: 24px; border-top: 1px solid var(--color-surface-container-high);">
						<button
							type="submit"
							class="btn-primary"
							style="width: 100%; justify-content: center;"
							disabled={isSubmitting || isLoadingBalance || !amount}
						>
							{#if isSubmitting}
								<span class="material-icons spin" style="font-size: 16px;">autorenew</span>
								Processing...
							{:else}
								Authorize Transfer
								<span class="material-icons" style="font-size: 16px;">arrow_forward</span>
							{/if}
						</button>
					</div>
					{#if errorMsg}
						<p class="text-error" style="margin: 16px 0 0;">{errorMsg}</p>
					{/if}
				</form>
			{/if}
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

	.loan-body {
		padding: 56px 40px;
		display: flex;
		flex-direction: column;
		align-items: center;
		flex: 1;
	}

	.loan-header {
		text-align: center;
		margin-bottom: 48px;
	}

	.loan-form {
		width: 100%;
		background: var(--color-surface-container-lowest);
		padding: 40px;
		border: 1px solid var(--color-surface-container-high);
	}

	.form-grid {
		display: grid;
		grid-template-columns: 1fr;
		gap: 24px;
	}

	.transfer-tab {
		flex: 1;
		padding: 12px;
		background: transparent;
		border: none;
		font-family: var(--font-family);
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-on-surface-variant);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.transfer-tab.active {
		background: var(--color-on-surface);
		color: var(--color-surface);
	}

	.submitted-state {
		text-align: center;
		padding: 80px 0;
	}

	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}
	@keyframes spin {
		from { transform: rotate(0deg); }
		to   { transform: rotate(360deg); }
	}

	@media (max-width: 768px) {
		.loan-body { padding: 32px 20px; }
		.loan-form { padding: 24px; border: none; background: transparent; }
	}
</style>
