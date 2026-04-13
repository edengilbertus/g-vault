<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { createWithdrawal, fetchDashboardSummary } from '$lib/api/client';
	import { getStoredToken } from '$lib/auth/session';
	import MemberNav from '$lib/components/MemberNav.svelte';

	let destinationType = $state('bank'); // 'bank' or 'mobile'
	let amount = $state('');
	
	// Bank fields
	let bankName = $state('');
	let accountNumber = $state('');
	let routingNumber = $state('');

	// Mobile fields
	let mobileNetwork = $state('');
	let phoneNumber = $state('');

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
		} catch (error) {
			errorMsg = error instanceof Error ? error.message : 'Unable to load account balance.';
		} finally {
			isLoadingBalance = false;
		}
	}

	async function handleWithdrawal(e: SubmitEvent) {
		e.preventDefault();
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}
		const withdrawalAmount = Number(amount);
		if (!withdrawalAmount || withdrawalAmount <= 0) {
			errorMsg = 'Enter a valid withdrawal amount.';
			return;
		}
		if (withdrawalAmount > availableBalance) {
			errorMsg = 'Insufficient balance for withdrawal.';
			return;
		}

		errorMsg = '';
		isSubmitting = true;
		try {
			const response = await createWithdrawal(token, {
				destination_type: destinationType as 'bank' | 'mobile',
				amount: withdrawalAmount,
				bank_name: destinationType === 'bank' ? bankName.trim() : undefined,
				account_number: destinationType === 'bank' ? accountNumber.trim() : undefined,
				routing_number: destinationType === 'bank' ? routingNumber.trim() : undefined,
				mobile_network:
					destinationType === 'mobile' ? (mobileNetwork as 'mtn' | 'airtel') : undefined,
				phone_number: destinationType === 'mobile' ? phoneNumber.trim() : undefined
			});
			referenceId = response.transaction.reference;
			availableBalance = Number(response.new_balance);
			submitted = true;
		} catch (error) {
			errorMsg = error instanceof Error ? error.message : 'Withdrawal failed.';
		} finally {
			isSubmitting = false;
		}
	}

	onMount(() => {
		void loadBalance();
	});
</script>

<svelte:head>
	<title>G Vault | Withdrawal</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="withdrawal" />

	<div class="main-content">
		<div class="loan-body">

			{#if submitted}
				<div class="submitted-state animate-fade-up">
					<span class="material-icons" style="font-size: 48px; color: #1a7f37; margin-bottom: 24px; display: block;">check_circle_outline</span>
					<h1 class="font-headline-lg" style="margin: 0 0 16px;">Withdrawal Processing</h1>
					<p style="color: var(--color-on-surface-variant); margin: 0 0 32px; font-size: 0.9375rem; line-height: 1.6;">
						Your withdrawal of <strong>UGX {Number(amount).toLocaleString('en-UG')}</strong> has been initiated. Funds will be available in {destinationType === 'bank' ? '1-3 business days' : 'a few minutes'}.
					</p>
					<p class="font-label" style="margin: 0 0 8px;">Reference ID</p>
					<p style="font-size: 1.5rem; font-weight: 800; letter-spacing: 0.08em; margin: 0 0 40px; font-family: monospace;">{referenceId}</p>
					
					<div style="display: flex; gap: 16px; justify-content: center;">
						<a href="/dashboard" class="btn-primary">Return to Dashboard</a>
					</div>
				</div>
			{:else}
				<div class="loan-header animate-fade-up stagger-1">
					<div>
						<p class="font-label" style="margin: 0 0 8px; color: var(--color-on-surface-variant);">Funds Management</p>
						<h1 class="font-display" style="margin: 0;">WITHDRAW<br />CAPITAL</h1>
					</div>
				</div>

				<form onsubmit={handleWithdrawal} class="loan-form animate-fade-up stagger-2" style="max-width: 540px;">
					
					<div class="input-group" style="margin-bottom: 32px;">
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
							style="font-size: 2rem; padding: 20px;"
						/>
						<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 8px 0 0;">
							{isLoadingBalance ? 'Loading available balance...' : `Available Balance: ${formatMoney(availableBalance)}`}
						</p>
					</div>

					<p class="font-label" style="margin: 0 0 16px;">Destination</p>
					<div style="display: flex; gap: 2px; margin-bottom: 24px; background: var(--color-surface-container-low); padding: 4px;">
						<button 
							type="button"
							class="transfer-tab {destinationType === 'bank' ? 'active' : ''}" 
							onclick={() => destinationType = 'bank'}
						>
							Bank Account
						</button>
						<button 
							type="button"
							class="transfer-tab {destinationType === 'mobile' ? 'active' : ''}" 
							onclick={() => destinationType = 'mobile'}
						>
							Mobile Money
						</button>
					</div>

					<div class="form-grid">
						{#if destinationType === 'bank'}
							<div class="input-group" style="grid-column: 1 / -1;">
								<label for="bank" class="input-label">Bank Name</label>
								<input id="bank" type="text" class="input-field" placeholder="e.g. Stanbic Bank Uganda" bind:value={bankName} required />
							</div>
							<div class="input-group">
								<label for="acc" class="input-label">Account Number</label>
								<input id="acc" type="text" class="input-field" bind:value={accountNumber} required />
							</div>
							<div class="input-group">
								<label for="route" class="input-label">Routing / SWIFT</label>
								<input id="route" type="text" class="input-field" bind:value={routingNumber} required />
							</div>
						{:else}
							<div class="input-group" style="grid-column: 1 / -1;">
								<label for="network" class="input-label">Mobile Network</label>
								<select id="network" class="select-field" bind:value={mobileNetwork} required>
									<option value="">Select network...</option>
									<option value="mtn">MTN Mobile Money</option>
									<option value="airtel">Airtel Money</option>
								</select>
							</div>
							<div class="input-group" style="grid-column: 1 / -1;">
								<label for="phone" class="input-label">Mobile Number</label>
								<input id="phone" type="tel" class="input-field" placeholder="+256..." bind:value={phoneNumber} required />
							</div>
						{/if}
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
								Authorize Withdrawal
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
		grid-template-columns: 1fr 1fr;
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
		.form-grid { grid-template-columns: 1fr; }
	}
</style>
