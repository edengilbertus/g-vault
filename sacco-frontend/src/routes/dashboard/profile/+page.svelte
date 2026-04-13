<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { me, updateProfile } from '$lib/api/client';
	import { getStoredToken, getStoredUser, persistSession } from '$lib/auth/session';
	import MemberNav from '$lib/components/MemberNav.svelte';

	let activeSection = $state('personal'); // 'personal', 'kyc', 'security'

	let fullName = $state('');
	let email = $state('');
	let phone = $state('');
	let nationalId = $state('');

	let isLoading = $state(true);
	let isSaving = $state(false);
	let saveSuccess = $state(false);
	let saveError = $state('');

	async function loadProfile() {
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		isLoading = true;
		try {
			const user = await me(token);
			fullName = user.full_name;
			email = user.email;
			phone = user.phone_number;
			nationalId = user.national_id ?? '';
		} catch {
			// Fall back to stored session data
			const stored = getStoredUser();
			if (stored) {
				fullName = stored.full_name;
				email = stored.email;
				phone = stored.phone_number;
				nationalId = stored.national_id ?? '';
			}
		} finally {
			isLoading = false;
		}
	}

	async function saveProfile(e: SubmitEvent) {
		e.preventDefault();
		const token = getStoredToken();
		if (!token) {
			goto('/');
			return;
		}

		saveError = '';
		saveSuccess = false;
		isSaving = true;
		try {
			const updated = await updateProfile(token, {
				full_name: fullName.trim(),
				email: email.trim(),
				phone_number: phone.trim(),
				national_id: nationalId.trim() || undefined
			});
			// Update the local session so the sidebar and other pages reflect the change
			persistSession(token, updated);
			saveSuccess = true;
			setTimeout(() => (saveSuccess = false), 3000);
		} catch (error) {
			saveError = error instanceof Error ? error.message : 'Unable to save profile changes.';
		} finally {
			isSaving = false;
		}
	}

	onMount(() => {
		void loadProfile();
	});
</script>

<svelte:head>
	<title>G Vault | Member Profile</title>
</svelte:head>

<div class="page-wrap">
	<MemberNav active="profile" />

	<div class="main-content">
		<div class="dashboard-body">
			<div class="section-header animate-fade-up stagger-1">
				<h1 class="font-display" style="margin: 0;">MEMBER<br />PROFILE</h1>
			</div>

			<div class="profile-layout animate-fade-up stagger-2" style="margin-top: 48px;">
				<!-- Sidebar Nav -->
				<div class="profile-sidebar">
					<button class="menu-item {activeSection === 'personal' ? 'active' : ''}" onclick={() => activeSection = 'personal'}>
						<span class="material-icons">person</span> Personal Details
					</button>
					<button class="menu-item {activeSection === 'kyc' ? 'active' : ''}" onclick={() => activeSection = 'kyc'}>
						<span class="material-icons">verified_user</span> KYC & Documents
					</button>
					<button class="menu-item {activeSection === 'security' ? 'active' : ''}" onclick={() => activeSection = 'security'}>
						<span class="material-icons">shield</span> Security
					</button>
				</div>

				<!-- Content Area -->
				<div class="profile-content">
					{#if activeSection === 'personal'}
						<p class="font-label" style="margin: 0 0 24px;">Personal Information</p>

						{#if isLoading}
							<p style="color: var(--color-on-surface-variant);">Loading profile...</p>
						{:else}
							<form onsubmit={saveProfile} class="form-grid">
								<div class="input-group" style="grid-column: 1 / -1;">
									<label for="fname" class="input-label">Full Name</label>
									<input id="fname" type="text" class="input-field" bind:value={fullName} required />
								</div>
								<div class="input-group">
									<label for="email" class="input-label">Email Address</label>
									<input id="email" type="email" class="input-field" bind:value={email} required />
								</div>
								<div class="input-group">
									<label for="phone" class="input-label">Phone Number</label>
									<input id="phone" type="tel" class="input-field" bind:value={phone} required />
								</div>
								<div class="input-group" style="grid-column: 1 / -1;">
									<label for="nid" class="input-label">National ID</label>
									<input id="nid" type="text" class="input-field" bind:value={nationalId} placeholder="Optional" />
								</div>

								{#if saveError}
									<p class="text-error" style="grid-column: 1 / -1; margin: 0;">{saveError}</p>
								{/if}
								{#if saveSuccess}
									<p style="grid-column: 1 / -1; margin: 0; color: #1a7f37; font-size: 0.8125rem; font-weight: 600;">
										<span class="material-icons" style="font-size: 14px; vertical-align: middle;">check_circle</span>
										Profile updated successfully.
									</p>
								{/if}

								<div style="grid-column: 1 / -1; margin-top: 16px;">
									<button type="submit" class="btn-primary" disabled={isSaving}>
										{#if isSaving}
											<span class="material-icons spin" style="font-size: 16px;">autorenew</span> Saving...
										{:else}
											Save Changes
										{/if}
									</button>
								</div>
							</form>
						{/if}

					{:else if activeSection === 'kyc'}
						<p class="font-label" style="margin: 0 0 24px;">KYC Status</p>

						<div style="background: var(--color-surface-container-low); padding: 24px; margin-bottom: 32px; display: flex; justify-content: space-between; align-items: center;">
							<div>
								<p style="margin: 0 0 8px; font-weight: 600;">Verification Level 3 (Maximum)</p>
								<p style="margin: 0; font-size: 0.8125rem; color: var(--color-on-surface-variant);">All account limits have been removed.</p>
							</div>
							<span class="badge badge-success">Verified</span>
						</div>

						<p class="font-label" style="margin: 0 0 16px;">Identity Documents</p>
						<div style="display: flex; flex-direction: column; gap: 1px; background: var(--color-surface-container-high);">
							<div class="doc-row">
								<div style="display: flex; align-items: center; gap: 12px;">
									<span class="material-icons" style="color: var(--color-on-surface-variant);">badge</span>
									<span>National ID Card</span>
								</div>
								<span class="badge badge-success">Approved</span>
							</div>
							<div class="doc-row">
								<div style="display: flex; align-items: center; gap: 12px;">
									<span class="material-icons" style="color: var(--color-on-surface-variant);">description</span>
									<span>Proof of Address (Utility Bill)</span>
								</div>
								<span class="badge badge-success">Approved</span>
							</div>
						</div>

						<button class="btn-secondary" style="margin-top: 24px;">Update Documents</button>

					{:else if activeSection === 'security'}
						<p class="font-label" style="margin: 0 0 24px;">Password</p>
						<button class="btn-secondary" style="margin-bottom: 48px;">Change Password</button>

						<p class="font-label" style="margin: 0 0 24px;">Two-Factor Authentication (2FA)</p>
						<div style="background: var(--color-surface-container-low); padding: 24px; margin-bottom: 24px;">
							<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
								<p style="margin: 0; font-weight: 600;">Authenticator App</p>
								<span class="badge badge-success">Enabled</span>
							</div>
							<p style="margin: 0; font-size: 0.8125rem; color: var(--color-on-surface-variant);">Used for sign in and authorizing outbound transfers.</p>
						</div>

						<button class="btn-ghost" style="color: var(--color-error);">Disable 2FA</button>
					{/if}
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

	.profile-layout {
		display: grid;
		grid-template-columns: 240px 1fr;
		gap: 64px;
	}

	.profile-sidebar {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.menu-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 16px;
		background: transparent;
		border: none;
		text-align: left;
		font-family: var(--font-family);
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-on-surface-variant);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.menu-item:hover {
		background: var(--color-surface-container-low);
	}

	.menu-item.active {
		background: var(--color-surface-container);
		color: var(--color-on-surface);
	}

	.menu-item .material-icons {
		font-size: 18px;
	}

	.profile-content {
		max-width: 600px;
	}

	.form-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 24px;
	}

	.doc-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 20px;
		background: var(--color-surface-container-lowest);
		font-size: 0.875rem;
		font-weight: 500;
	}

	:global(.spin) {
		animation: spin 0.8s linear infinite;
	}
	@keyframes spin {
		from { transform: rotate(0deg); }
		to   { transform: rotate(360deg); }
	}

	@media (max-width: 768px) {
		.dashboard-body { padding: 32px 20px; }
		.profile-layout { grid-template-columns: 1fr; gap: 40px; }
		.form-grid { grid-template-columns: 1fr; }
	}
</style>
