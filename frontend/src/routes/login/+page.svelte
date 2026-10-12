<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { KeyRound } from '@lucide/svelte';
	import Button from '#lib/components/Button.svelte';
	import { sessionUser } from '../../lib/stores/session';
	import { login } from '../../lib/stores/session';
	import { conditionalPasskeyLogin, loginWithPasskey, webAuthnSupported } from '../../lib/webauthn';

	let email = $state('');
	let password = $state('');
	let message = $state<string | null>(null);
	let saving = $state(false);
	let passkeyBusy = $state(false);
	let canPasskey = $state(false);

	const inputClass = 'min-h-11 w-full rounded-[12px] border border-line bg-bg px-3';

	function isCancel(error: unknown): boolean {
		return error instanceof DOMException && error.name === 'NotAllowedError';
	}

	async function onPasskey() {
		passkeyBusy = true;
		message = null;
		try {
			const user = await loginWithPasskey();
			sessionUser.set(user);
			await goto('/');
		} catch (error) {
			if (!isCancel(error)) message = 'No se pudo iniciar sesión con passkey.';
		} finally {
			passkeyBusy = false;
		}
	}

	async function onSubmit(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		message = null;
		const error = await login(email, password);
		saving = false;
		if (error) {
			message = error;
		} else {
			await goto('/');
		}
	}

	onMount(async () => {
		canPasskey = webAuthnSupported();
		if (!canPasskey) return;
		try {
			// Sugerencia de passkey vía autocompletado (si el dispositivo la tiene).
			const user = await conditionalPasskeyLogin();
			if (user) {
				sessionUser.set(user);
				await goto('/');
			}
		} catch {
			/* el usuario no eligió passkey o no hay: se ignora */
		}
	});
</script>

<div class="mx-auto flex min-h-[80vh] max-w-sm flex-col justify-center">
	<div class="rounded-brand-lg border border-line bg-surface p-6 shadow-sm">
		<div class="flex flex-col items-center text-center">
			<img src="/brand/logo-mark.png" alt="HAPMED" class="h-16 w-16" />
			<span class="mt-3 text-[20px] font-bold tracking-[0.22em] text-ink">HAPMED</span>
			<p class="mt-1 text-[13px] text-ink-2">Engineering what comes next.</p>
		</div>

		<h1 class="mt-6 text-[20px] font-semibold">Iniciar sesión</h1>
		<p class="mt-1 text-[14px] text-ink-2">Panel de administración EVAS.</p>

		{#if canPasskey}
			<button
				type="button"
				class="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-[12px] bg-accent px-4 text-[15px] font-medium text-white hover:opacity-90"
				disabled={passkeyBusy}
				onclick={onPasskey}
			>
				<KeyRound size={18} aria-hidden="true" />
				{passkeyBusy ? 'Esperando passkey…' : 'Entrar con passkey'}
			</button>
			<p class="mt-2 text-center text-[12px] text-ink-3">o usa tu contraseña</p>
		{/if}

		<form class="mt-3 flex flex-col gap-3" onsubmit={onSubmit}>
			<label class="flex flex-col gap-1 text-[14px]">
				<span>Correo</span>
				<input
					type="email"
					bind:value={email}
					required
					autocomplete="username webauthn"
					class={inputClass}
				/>
			</label>
			<label class="flex flex-col gap-1 text-[14px]">
				<span>Contraseña</span>
				<input
					type="password"
					bind:value={password}
					required
					autocomplete="current-password"
					class={inputClass}
				/>
			</label>
			<Button type="submit" variant="secondary" disabled={saving}>
				{saving ? 'Entrando…' : 'Entrar con contraseña'}
			</Button>
		</form>

		{#if message}
			<p role="alert" class="mt-3 text-[13px] text-danger">{message}</p>
		{/if}
	</div>
</div>
