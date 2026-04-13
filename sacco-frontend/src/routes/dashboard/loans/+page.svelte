<script lang="ts">
	import MemberNav from '$lib/components/MemberNav.svelte';

	let currentStep = $state(1);
	const totalSteps = 5;

	const stepLabels = [
		'Personal Details',
		'Financial Intent',
		'Collateral',
		'Documentation',
		'Review & Submit'
	];

	// Form state
	let loanAmount = $state('');
	let loanPurpose = $state('');
	let loanTerm = $state('12');
	let firstName = $state('');
	let lastName = $state('');
	let idNumber = $state('');
	let employer = $state('');
	let salary = $state('');
	let collateralType = $state('');
	let collateralValue = $state('');
	let agreed = $state(false);
	let isSubmitting = $state(false);
	let submitted = $state(false);
	let filesUploaded = $state(false);

	function validateStep() {
		if (currentStep === 1) return firstName.trim() !== '' && lastName.trim() !== '' && idNumber.trim() !== '';
		if (currentStep === 2) return loanAmount !== '' && loanPurpose !== '' && loanTerm !== '';
		if (currentStep === 3) return collateralType !== '';
		if (currentStep === 4) return filesUploaded;
		return true;
	}

	function nextStep() {
		if (!validateStep()) {
			alert('Please complete all required fields for this step.');
			return;
		}
		if (currentStep < totalSteps) currentStep++;
	}

	function prevStep() {
		if (currentStep > 1) currentStep--;
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		isSubmitting = true;
		await new Promise((r) => setTimeout(r, 1500));
		isSubmitting = false;
		submitted = true;
	}

	const presetAmounts = [500000, 1000000, 2500000, 5000000, 10000000];
</script>

<svelte:head>
	<title>G Vault | Loan Application</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="loans" />

	<div class="main-content">
		<div class="loan-body">

			{#if submitted}
				<!-- Success state -->
				<div class="submitted-state animate-fade-up">
					<span class="material-icons" style="font-size: 48px; color: #1a7f37; margin-bottom: 24px; display: block;">check_circle_outline</span>
					<h1 class="font-headline-lg" style="margin: 0 0 16px;">Application Submitted</h1>
					<p style="color: var(--color-on-surface-variant); margin: 0 0 32px; font-size: 0.9375rem; line-height: 1.6;">
						Your loan application has been received and is under automated review. You will be contacted within 1–3 business days.
					</p>
					<p class="font-label" style="margin: 0 0 8px;">Reference Number</p>
					<p style="font-size: 1.5rem; font-weight: 800; letter-spacing: 0.08em; margin: 0 0 40px;">LN-2024-{Math.floor(Math.random() * 90000) + 10000}</p>
					<a href="/dashboard" class="btn-primary">
						<span class="material-icons" style="font-size: 16px;">arrow_back</span>
						Return to Dashboard
					</a>
				</div>

			{:else}
				<!-- Header -->
				<div class="loan-header animate-fade-up stagger-1">
					<div>
						<p class="font-label" style="margin: 0 0 8px; color: var(--color-on-surface-variant);">
							Step {String(currentStep).padStart(2, '0')} of {String(totalSteps).padStart(2, '0')} — {stepLabels[currentStep - 1]}
						</p>
						<h1 class="font-headline-lg" style="margin: 0;">
							{#if currentStep === 1}Who are you?
							{:else if currentStep === 2}How much capital do you require?
							{:else if currentStep === 3}What collateral can you offer?
							{:else if currentStep === 4}Documentation
							{:else}Review & Submit{/if}
						</h1>
						<p style="color: var(--color-on-surface-variant); margin: 8px 0 0; font-size: 0.875rem; line-height: 1.6; max-width: 520px;">
							{#if currentStep === 2}
								Specify the total amount in UGX. Our automated risk assessment will evaluate this against your current liquidity.
							{:else if currentStep === 1}
								Provide your personal identification details to begin the application process.
							{:else if currentStep === 3}
								List the assets you are prepared to offer as security for the loan.
							{:else if currentStep === 4}
								Upload supporting documents required for the application.
							{:else}
								Review all details before final submission. This cannot be undone.
							{/if}
						</p>
					</div>
					<div style="display: flex; align-items: center; gap: 12px;">
						{#if currentStep > 1}
							<button class="btn-ghost" onclick={prevStep}>
								<span class="material-icons" style="font-size: 16px;">arrow_back</span>
								Back
							</button>
						{/if}
					</div>
				</div>

				<!-- Progress -->
				<div class="step-progress animate-fade-up stagger-2">
					{#each stepLabels as label, i}
						<div class="step-item" class:step-done={i + 1 < currentStep} class:step-active={i + 1 === currentStep}>
							<div class="step-dot">
								{#if i + 1 < currentStep}
									<span class="material-icons" style="font-size: 12px;">check</span>
								{:else}
									{i + 1}
								{/if}
							</div>
							<span class="step-label">{label}</span>
						</div>
						{#if i < stepLabels.length - 1}
							<div class="step-line" class:step-line-done={i + 1 < currentStep}></div>
						{/if}
					{/each}
				</div>

				<!-- Form Area -->
				<form onsubmit={handleSubmit} class="loan-form animate-fade-up stagger-3">

					{#if currentStep === 1}
						<div class="form-grid">
							<div class="input-group">
								<label for="first-name" class="input-label">First Name</label>
								<input id="first-name" type="text" class="input-field" placeholder="Julian" bind:value={firstName} required />
							</div>
							<div class="input-group">
								<label for="last-name" class="input-label">Last Name</label>
								<input id="last-name" type="text" class="input-field" placeholder="Thorne" bind:value={lastName} required />
							</div>
							<div class="input-group">
								<label for="id-number" class="input-label">National ID Number</label>
								<input id="id-number" type="text" class="input-field" placeholder="ID / Passport Number" bind:value={idNumber} required />
							</div>
							<div class="input-group">
								<label for="employer" class="input-label">Current Employer</label>
								<input id="employer" type="text" class="input-field" placeholder="Company Name" bind:value={employer} />
							</div>
							<div class="input-group">
								<label for="salary" class="input-label">Monthly Net Salary (UGX)</label>
								<input id="salary" type="number" class="input-field" placeholder="0.00" bind:value={salary} min="0" />
							</div>
						</div>

					{:else if currentStep === 2}
						<!-- Preset amounts -->
						<div>
							<p class="input-label" style="margin-bottom: 12px;">Select a preset amount</p>
							<div class="preset-amounts">
								{#each presetAmounts as amt}
									<button
										type="button"
										class="amount-btn"
										class:selected={loanAmount === String(amt)}
										onclick={() => (loanAmount = String(amt))}
									>
										UGX {amt.toLocaleString('en-UG')}
									</button>
								{/each}
							</div>
						</div>

						<div class="input-group" style="margin-top: 24px;">
							<label for="loan-amount" class="input-label">Or Enter Custom Amount (UGX)</label>
							<input
								id="loan-amount"
								type="number"
								class="input-field"
								placeholder="0"
								bind:value={loanAmount}
								min="50000"
								max="500000000"
								step="1"
								required
							/>
						</div>

						<div class="input-group" style="margin-top: 24px;">
							<label for="loan-purpose" class="input-label">Purpose of Loan</label>
							<select id="loan-purpose" class="select-field" bind:value={loanPurpose} required>
								<option value="">Select purpose...</option>
								<option value="business">Business Expansion</option>
								<option value="education">Education</option>
								<option value="medical">Medical</option>
								<option value="real_estate">Real Estate</option>
								<option value="personal">Personal</option>
							</select>
						</div>

						<div class="input-group" style="margin-top: 24px;">
							<label for="loan-term" class="input-label">Repayment Term</label>
							<select id="loan-term" class="select-field" bind:value={loanTerm} required>
								<option value="6">6 months</option>
								<option value="12">12 months</option>
								<option value="24">24 months</option>
								<option value="36">36 months</option>
								<option value="48">48 months</option>
								<option value="60">60 months</option>
							</select>
						</div>

						{#if loanAmount && loanTerm}
							<div class="loan-summary">
								<p class="font-label" style="margin: 0 0 16px;">Estimated Repayment</p>
								<div style="display: flex; gap: 32px; flex-wrap: wrap;">
									<div>
										<p class="stat-label">Monthly Payment</p>
										<p class="stat-value">UGX {Math.round(Number(loanAmount) * 1.18 / Number(loanTerm)).toLocaleString('en-UG')}</p>
									</div>
									<div>
										<p class="stat-label">Total Repayable</p>
										<p class="stat-value">UGX {Math.round(Number(loanAmount) * 1.18).toLocaleString('en-UG')}</p>
									</div>
									<div>
										<p class="stat-label">Interest Rate</p>
										<p class="stat-value">18.0% APR</p>
									</div>
								</div>
							</div>
						{/if}

					{:else if currentStep === 3}
						<div class="input-group">
							<label for="collateral-type" class="input-label">Collateral Type</label>
							<select id="collateral-type" class="select-field" bind:value={collateralType} required>
								<option value="">Select type...</option>
								<option value="property">Real Property</option>
								<option value="vehicle">Motor Vehicle</option>
								<option value="shares">Shares / Securities</option>
								<option value="equipment">Equipment</option>
								<option value="other">Other</option>
							</select>
						</div>

						<div class="input-group" style="margin-top: 24px;">
							<label for="collateral-value" class="input-label">Estimated Value (UGX)</label>
							<input id="collateral-value" type="number" class="input-field" placeholder="Market value" bind:value={collateralValue} min="0" />
						</div>

						<div class="input-group" style="margin-top: 24px;">
							<label for="collateral-desc" class="input-label">Description</label>
							<textarea id="collateral-desc" class="input-field" placeholder="Provide a brief description of the collateral asset..." rows="4"></textarea>
						</div>

					{:else if currentStep === 4}
						<div class="upload-zone" class:upload-active={filesUploaded}>
							<span class="material-icons" style="font-size: 40px; color: {filesUploaded ? '#1a7f37' : 'var(--color-on-surface-variant)'}; margin-bottom: 16px;">
								{filesUploaded ? 'check_circle' : 'upload_file'}
							</span>
							<p style="font-size: 0.875rem; font-weight: 600; margin: 0 0 8px; color: var(--color-on-surface);">
								{filesUploaded ? 'Documents uploaded successfully' : 'Drag & drop documents here'}
							</p>
							<p style="font-size: 0.75rem; color: var(--color-on-surface-variant); margin: 0 0 20px;">
								{filesUploaded ? 'Total size: 4.2 MB' : 'PDF, JPG, PNG — max 10MB each'}
							</p>
							{#if !filesUploaded}
								<button type="button" class="btn-secondary" onclick={() => filesUploaded = true}>Simulate Upload</button>
							{/if}
						</div>

						<div style="margin-top: 24px;">
							<p class="font-label" style="margin: 0 0 16px;">Required Documents</p>
							{#each ['National ID / Passport', 'Proof of Income (3 months)', 'Bank Statements (6 months)', 'Collateral Documentation'] as doc}
								<div style="display: flex; align-items: center; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--color-surface-container-high);">
									<span class="material-icons" style="font-size: 18px; color: {filesUploaded ? '#1a7f37' : 'var(--color-on-surface-variant)'};">
										{filesUploaded ? 'task_alt' : 'description'}
									</span>
									<span style="font-size: 0.875rem; color: var(--color-on-surface);">{doc}</span>
									<span class="badge {filesUploaded ? 'badge-success' : 'badge-pending'}" style="margin-left: auto;">
										{filesUploaded ? 'Completed' : 'Pending'}
									</span>
								</div>
							{/each}
						</div>

					{:else if currentStep === 5}
						<div class="review-grid">
							<div class="review-section">
								<p class="font-label" style="margin: 0 0 16px;">Personal Details</p>
								<div class="review-item"><span>Name</span><span>{firstName} {lastName}</span></div>
								<div class="review-item"><span>ID Number</span><span>{idNumber || '—'}</span></div>
								<div class="review-item"><span>Employer</span><span>{employer || '—'}</span></div>
								<div class="review-item"><span>Monthly Salary</span><span>{salary ? 'UGX ' + Number(salary).toLocaleString('en-UG') : '—'}</span></div>
							</div>
							<div class="review-section">
								<p class="font-label" style="margin: 0 0 16px;">Loan Details</p>
								<div class="review-item"><span>Amount</span><span>{loanAmount ? 'UGX ' + Number(loanAmount).toLocaleString('en-UG') : '—'}</span></div>
								<div class="review-item"><span>Purpose</span><span>{loanPurpose || '—'}</span></div>
								<div class="review-item"><span>Term</span><span>{loanTerm} months</span></div>
								<div class="review-item"><span>Rate</span><span>18.0% APR</span></div>
							</div>
						</div>

						<div style="display: flex; align-items: flex-start; gap: 12px; margin-top: 32px; padding: 24px; background: var(--color-surface-container-low);">
							<input
								type="checkbox"
								id="agreed"
								class="checkbox-field"
								bind:checked={agreed}
								required
							/>
							<label for="agreed" style="font-size: 0.8125rem; color: var(--color-on-surface-variant); line-height: 1.6; cursor: pointer;">
								I confirm that all information provided is accurate and complete. I authorise G Vault to conduct a credit assessment and contact the references provided.
							</label>
						</div>
					{/if}

					<!-- Navigation -->
					<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 48px;">
						{#if currentStep > 1}
							<button type="button" class="btn-ghost" onclick={prevStep}>
								<span class="material-icons" style="font-size: 16px;">arrow_back</span>
								Back
							</button>
						{:else}
							<div></div>
						{/if}

						{#if currentStep < totalSteps}
							<button type="button" class="btn-primary" onclick={nextStep}>
								Continue
								<span class="material-icons" style="font-size: 16px;">arrow_forward</span>
							</button>
						{:else}
							<button type="submit" class="btn-primary" disabled={!agreed || isSubmitting}>
								{#if isSubmitting}
									<span class="material-icons spin" style="font-size: 16px;">autorenew</span>
									Submitting...
								{:else}
									Submit Application
									<span class="material-icons" style="font-size: 16px;">send</span>
								{/if}
							</button>
						{/if}
					</div>
				</form>
			{/if}
		</div>

		<footer class="footer">
			<p class="font-label" style="margin: 0;">© 2024 G VAULT</p>
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
		flex: 1;
	}

	.loan-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 40px;
	}

	/* Step progress indicator */
	.step-progress {
		display: flex;
		align-items: center;
		margin-bottom: 48px;
	}

	.step-item {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
	}

	.step-dot {
		width: 28px;
		height: 28px;
		background: var(--color-surface-container);
		color: var(--color-on-surface-variant);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.6875rem;
		font-weight: 700;
		flex-shrink: 0;
	}

	.step-active .step-dot {
		background: var(--color-primary);
		color: white;
	}

	.step-done .step-dot {
		background: var(--color-primary-container);
		color: white;
	}

	.step-label {
		font-size: 0.6875rem;
		font-weight: 600;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--color-on-surface-variant);
		white-space: nowrap;
	}

	.step-active .step-label,
	.step-done .step-label {
		color: var(--color-on-surface);
	}

	.step-line {
		flex: 1;
		height: 1px;
		background: var(--color-surface-container-high);
		margin: 0 8px;
	}

	.step-line-done {
		background: var(--color-primary-container);
	}

	/* Form */
	.loan-form {
		max-width: 640px;
	}

	.form-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
	}

	/* Preset amounts */
	.preset-amounts {
		display: flex;
		gap: 2px;
		flex-wrap: wrap;
	}

	/* Loan summary box */
	.loan-summary {
		margin-top: 32px;
		background: var(--color-surface-container-low);
		padding: 24px;
	}

	/* Upload zone */
	.upload-zone {
		background: var(--color-surface-container-low);
		padding: 56px 32px;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		border: 2px dashed var(--color-outline-variant) !important;
		border-radius: 0 !important;
	}

	/* Review grid */
	.review-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 32px;
	}

	.review-section {
		background: var(--color-surface-container-lowest);
		padding: 24px;
	}

	.review-item {
		display: flex;
		justify-content: space-between;
		padding: 12px 0;
		border-bottom: 1px solid var(--color-surface-container);
		font-size: 0.875rem;
	}

	.review-item span:first-child {
		color: var(--color-on-surface-variant);
		text-transform: uppercase;
		letter-spacing: 0.04em;
		font-size: 0.6875rem;
		font-weight: 600;
	}

	.review-item span:last-child {
		font-weight: 600;
		color: var(--color-on-surface);
	}

	/* Submitted */
	.submitted-state {
		max-width: 480px;
		margin: 0 auto;
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
		.form-grid { grid-template-columns: 1fr; }
		.review-grid { grid-template-columns: 1fr; }
		.step-label { display: none; }
	}
</style>
