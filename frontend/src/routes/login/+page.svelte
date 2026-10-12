<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '#lib/components/Button.svelte';
	import { login } from '../../lib/stores/session';

	let email = $state('');
	let password = $state('');
	let message = $state<string | null>(null);
	let saving = $state(false);

	const inputClass = 'min-h-11 w-full rounded-[12px] border border-line bg-bg px-3';

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

		<form class="mt-5 flex flex-col gap-3" onsubmit={onSubmit}>
			<label class="flex flex-col gap-1 text-[14px]">
				<span>Correo</span>
				<input
					type="email"
					bind:value={email}
					required
					autocomplete="username"
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
			<Button type="submit" variant="primary" disabled={saving}>
				{saving ? 'Entrando…' : 'Entrar'}
			</Button>
		</form>

		{#if message}
			<p role="alert" class="mt-3 text-[13px] text-danger">{message}</p>
		{/if}
	</div>
</div>
