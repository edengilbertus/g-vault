<script lang="ts">
	let { data } = $props();
	
	// Optional snippet to showcase different CMS-like content
	const contentMap: Record<string, { title: string, body: string }> = {
		privacy: {
			title: 'PRIVACY POLICY',
			body: '<p>The G Vault Editorial (“The G Vault”) respects your privacy. This Privacy Policy describes how we collect, use, and share your personal information when you use our services.</p><h3>1. Information Collection</h3><p>We collect information you provide directly to us (e.g., identity verification data, communication records). We also automatically collect certain telemetry data related to your interface usage.</p><h3>2. Use of Information</h3><p>We use the information we collect to operate, maintain, and provide the features and functionality of our core banking systems. Your data may be used for risk profiling and algorithmic credit scoring.</p><h3>3. Data Sharing</h3><p>We do not share your personal data with third parties except as necessary to provide our services or as required by law enforcement under verified jurisdiction.</p>'
		},
		terms: {
			title: 'TERMS OF SERVICE',
			body: '<p>By accessing or using The G Vault Editorial Banking interface, you agree to be bound by these Terms.</p><h3>1. User Obligations</h3><p>You must provide accurate information during the KYC process. Any falsification may result in immediate account termination.</p><h3>2. Financial Liability</h3><p>You are solely responsible for all transaction authorizations made using your credentials. We process transfers exactly as instructed.</p><h3>3. Service Availability</h3><p>While we strive for 99.99% uptime, we do not guarantee uninterrupted access to the terminal interface during scheduled maintenance windows.</p>'
		},
		security: {
			title: 'SECURITY PROTOCOLS',
			body: '<p>Security is the foundational pillar of The G Vault architecture.</p><h3>1. Encryption Standard</h3><p>All data at rest is encrypted using AES-256. All transmission occurs over TLS 1.3 with forward secrecy.</p><h3>2. Authentication</h3><p>We strongly recommend configuring Time-based One-Time Passwords (TOTP) for all accounts. Biometric authorization is supported on compatible mobile hardware.</p><h3>3. Vulnerability Reporting</h3><p>If you believe you have discovered a vulnerability, please report it immediately to security@gvault.com. Do not publicly disclose the issue until our engineering team has remediated it.</p>'
		},
		accessibility: {
			title: 'ACCESSIBILITY STATEMENT',
			body: '<p>The G Vault Editorial is committed to ensuring digital accessibility for people with disabilities.</p><h3>1. Conformance Status</h3><p>We design our interfaces guided by the Web Content Accessibility Guidelines (WCAG) 2.1 level AA.</p><h3>2. High Contrast Design</h3><p>Our default architectural aesthetic relies heavily on high-contrast monochrome design, which inherently aids visibility. We continuously audit our color contrast ratios.</p><h3>3. Feedback</h3><p>If you encounter accessibility barriers, please contact our support team. We will work to provide the information in an alternative format.</p>'
		}
	};

	let pageContent = $derived(contentMap[data.slug] || { title: 'NOT FOUND', body: '<p>The requested document could not be located in the system.</p>' });
</script>

<svelte:head>
	<title>G Vault | {pageContent.title}</title>
</svelte:head>

<div class="page-wrap">
	<!-- Minimal Header -->
	<header class="header">
		<a href="/" class="brand-logo font-display">G VAULT.</a>
		<a href="/login" class="btn-ghost">Sign In</a>
	</header>

	<main class="main-content">
		<div class="content-wrapper animate-fade-up">
			<div class="document-header">
				<p class="font-label" style="margin: 0 0 16px; color: var(--color-on-surface-variant);">Legal & Compliance</p>
				<h1 class="font-display" style="margin: 0;">{pageContent.title}</h1>
				<p style="margin: 16px 0 0; font-size: 0.75rem; font-family: monospace; color: var(--color-on-surface-variant);">Last Updated: April 2024</p>
			</div>

			<div class="document-body">
				{@html pageContent.body}
			</div>

			<div style="margin-top: 64px;">
				<a href="javascript:history.back()" class="btn-secondary">
					<span class="material-icons" style="font-size: 16px;">arrow_back</span>
					Return Source
				</a>
			</div>
		</div>
	</main>

	<!-- Minimal Footer -->
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

<style>
	.page-wrap {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		background-color: var(--color-surface);
	}

	.header {
		padding: 24px 40px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: var(--color-surface-container-lowest);
		border-bottom: 1px solid var(--color-surface-container);
	}

	.brand-logo {
		font-size: 1rem;
		font-weight: 800;
		color: var(--color-on-surface);
		text-decoration: none;
		letter-spacing: 0.05em;
	}

	.main-content {
		flex: 1;
		display: flex;
		justify-content: center;
		padding: 80px 40px;
	}

	.content-wrapper {
		width: 100%;
		max-width: 680px;
	}

	.document-header {
		margin-bottom: 56px;
		padding-bottom: 32px;
		border-bottom: 2px solid var(--color-surface-container-high);
	}

	.document-body :global(p) {
		font-size: 0.9375rem;
		line-height: 1.7;
		color: var(--color-on-surface);
		margin: 0 0 24px;
	}

	.document-body :global(h3) {
		font-size: 1.125rem;
		font-weight: 700;
		margin: 40px 0 16px;
		color: var(--color-on-surface);
		text-transform: uppercase;
		letter-spacing: 0.02em;
	}

	@media (max-width: 768px) {
		.header { padding: 16px 20px; }
		.main-content { padding: 40px 20px; }
	}
</style>
