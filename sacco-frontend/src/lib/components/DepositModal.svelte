<script lang="ts">
	let { onclose } = $props<{ onclose: () => void }>();

	let selectedAmount = $state('');
	let customAmount = $state('');
	let paymentMethod = $state<'mtn' | 'airtel' | 'card' | 'bank'>('mtn');
	let phoneNumber = $state('');
	let step = $state<'select' | 'confirm' | 'processing' | 'success'>('select');

	const presets = [50000, 100000, 200000, 500000, 1000000];

	function selectPreset(amt: number) {
		selectedAmount = String(amt);
		customAmount = '';
	}

	function getAmount() {
		return customAmount ? Number(customAmount) : Number(selectedAmount);
	}

	async function handleContinue() {
		if (!getAmount()) return;
		step = 'confirm';
	}

	async function handleConfirm() {
		step = 'processing';
		await new Promise((r) => setTimeout(r, 2500));
		step = 'success';
	}

	function formatMoney(n: number) {
		return 'UGX ' + Math.round(n).toLocaleString('en-UG');
	}
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div class="modal-overlay animate-fade-in" onclick={(e) => { if (e.target === e.currentTarget) onclose(); }}>
	<div class="modal-panel animate-fade-up">

		{#if step === 'select'}
			<!-- Header -->
			<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px;">
				<div>
					<p class="font-label" style="margin: 0 0 6px;">Mobile Money</p>
					<h2 class="font-headline-md" style="margin: 0;">Deposit Funds</h2>
				</div>
				<button onclick={onclose} class="btn-ghost" aria-label="Close modal">
					<span class="material-icons" style="font-size: 20px;">close</span>
				</button>
			</div>

			<!-- Payment Method -->
			<div style="margin-bottom: 32px;">
				<p class="input-label" style="margin-bottom: 12px;">Payment Method</p>
				<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 2px;">
					{#each [
						{ id: 'mtn', label: 'MTN Mobile Money' },
						{ id: 'airtel', label: 'Airtel Money' },
						{ id: 'card', label: 'Card' },
						{ id: 'bank', label: 'Bank Transfer' },
					] as method}
						<button
							type="button"
							class="method-btn"
							class:method-active={paymentMethod === method.id}
							onclick={() => (paymentMethod = method.id as typeof paymentMethod)}
						>
							{method.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Preset Amounts -->
			<div style="margin-bottom: 24px;">
				<p class="input-label" style="margin-bottom: 12px;">Quick Select Amount</p>
				<div style="display: flex; gap: 2px; flex-wrap: wrap;">
					{#each presets as amt}
						<button
							type="button"
							class="amount-btn"
							class:selected={selectedAmount === String(amt) && !customAmount}
							onclick={() => selectPreset(amt)}
						>
							UGX {amt.toLocaleString('en-UG')}
						</button>
					{/each}
				</div>
			</div>

			<!-- Custom Amount -->
			<div class="input-group" style="margin-bottom: 24px;">
				<label for="deposit-amount" class="input-label">Enter Custom Amount (UGX)</label>
				<input
					id="deposit-amount"
					type="number"
					class="input-field"
					placeholder="0.00"
					bind:value={customAmount}
					min="1"
					oninput={() => (selectedAmount = '')}
				/>
			</div>

			<!-- Phone number for mobile money -->
			{#if paymentMethod === 'mtn' || paymentMethod === 'airtel'}
				<div class="input-group" style="margin-bottom: 32px;">
					<label for="phone-number" class="input-label">
						{paymentMethod === 'mtn' ? 'MTN Mobile Money' : 'Airtel Money'} Phone Number
					</label>
					<input
						id="phone-number"
						type="tel"
						class="input-field"
						placeholder="+256 700 000 000"
						bind:value={phoneNumber}
					/>
				</div>
			{/if}

			{#if getAmount() > 0}
				<div style="background: var(--color-surface-container-low); padding: 20px; margin-bottom: 32px; display: flex; justify-content: space-between; align-items: center;">
					<span class="font-label">Deposit Amount</span>
					<span style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;">{formatMoney(getAmount())}</span>
				</div>
			{/if}

			<button
				class="btn-primary"
				style="width: 100%; justify-content: center;"
				onclick={handleContinue}
				disabled={!getAmount()}
			>
				Continue
				<span class="material-icons" style="font-size: 16px;">arrow_forward</span>
			</button>

		{:else if step === 'confirm'}
			<div style="margin-bottom: 40px;">
				<p class="font-label" style="margin: 0 0 6px; color: var(--color-on-surface-variant);">Confirm Transaction</p>
				<h2 class="font-headline-md" style="margin: 0;">Review Details</h2>
			</div>

			<div style="background: var(--color-surface-container-low); padding: 0; margin-bottom: 32px;">
				{#each [
					{ label: 'Method', value: paymentMethod.toUpperCase() },
					{ label: 'Amount', value: formatMoney(getAmount()) },
					...(phoneNumber ? [{ label: 'Phone', value: phoneNumber }] : []),
					{ label: 'Destination', value: 'Savings — ****8450' },
					{ label: 'Processing Fee', value: 'UGX 0' },
				] as row}
					<div style="display: flex; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--color-surface-container);">
						<span class="font-label">{row.label}</span>
						<span style="font-weight: 700; font-size: 0.875rem;">{row.value}</span>
					</div>
				{/each}
			</div>

			<div style="display: flex; gap: 12px;">
				<button class="btn-secondary" style="flex: 1; justify-content: center;" onclick={() => (step = 'select')}>
					Back
				</button>
				<button class="btn-primary" style="flex: 2; justify-content: center;" onclick={handleConfirm}>
					Confirm Deposit
					<span class="material-icons" style="font-size: 16px;">check</span>
				</button>
			</div>

		{:else if step === 'processing'}
			<div style="text-align: center; padding: 40px 0;">
				<div class="processing-spinner">
					<span class="material-icons spin" style="font-size: 48px; color: var(--color-on-surface-variant);">autorenew</span>
				</div>
				<p class="font-label" style="margin: 24px 0 8px;">Processing Transaction</p>
				<p style="color: var(--color-on-surface-variant); font-size: 0.875rem; margin: 0;">
					{#if paymentMethod === 'mtn' || paymentMethod === 'airtel'}
						A payment request has been sent to {phoneNumber || 'your phone'}. Please approve on your device.
					{:else}
						Initiating secure transfer...
					{/if}
				</p>
			</div>

		{:else if step === 'success'}
			<div style="text-align: center; padding: 20px 0;">
				<span class="material-icons" style="font-size: 56px; color: #1a7f37; margin-bottom: 20px; display: block;">check_circle_outline</span>
				<h2 class="font-headline-md" style="margin: 0 0 12px;">Deposit Successful</h2>
				<p style="color: var(--color-on-surface-variant); margin: 0 0 32px; font-size: 0.875rem; line-height: 1.6;">
					{formatMoney(getAmount())} has been deposited to your Savings account. Funds are available immediately.
				</p>
				<p class="font-label" style="margin: 0 0 6px;">Transaction Reference</p>
				<p style="font-size: 1rem; font-weight: 800; letter-spacing: 0.08em; margin: 0 0 40px; font-family: monospace;">
					TXN-{Date.now().toString().slice(-8)}
				</p>
				<button class="btn-primary" style="width: 100%; justify-content: center;" onclick={onclose}>
					Done
					<span class="material-icons" style="font-size: 16px;">check</span>
				</button>
			</div>
		{/if}

	</div>
</div>

<style>
	.method-btn {
		background: var(--color-surface-container);
		border: none;
		padding: 12px 8px;
		font-family: var(--font-family);
		font-size: 0.625rem;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--color-on-surface-variant);
		cursor: pointer;
		transition: background-color 0.1s ease, color 0.1s ease;
	}

	.method-btn:hover {
		background: var(--color-surface-container-high);
		color: var(--color-on-surface);
	}

	.method-active {
		background: var(--color-primary) !important;
		color: white !important;
	}

	.processing-spinner {
		display: flex;
		justify-content: center;
		margin-bottom: 8px;
	}

	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}
	@keyframes spin {
		from { transform: rotate(0deg); }
		to   { transform: rotate(360deg); }
	}
</style>
