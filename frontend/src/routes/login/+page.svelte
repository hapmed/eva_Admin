<script lang="ts">
	import Button from '#lib/components/Button.svelte';

	let email = $state('');
	let password = $state('');
	let message = $state('');

	function onSubmit(event: SubmitEvent) {
		event.preventDefault();
		message = 'La autenticación se habilita en la Fase 3.';
	}
</script>

<div class="mx-auto flex min-h-[70vh] max-w-sm flex-col justify-center">
	<div class="rounded-brand-lg border border-line bg-surface p-6">
		<div class="flex items-center gap-2">
			<img src="/brand/logo-mark.png" alt="" class="h-9 w-9" />
			<span class="text-[17px] font-bold tracking-[0.18em]">HAPMED</span>
		</div>
		<h1 class="mt-4 text-[22px] font-semibold">Iniciar sesión</h1>
		<p class="mt-1 text-[14px] text-ink-2">Panel de administración EVAS.</p>

		<form class="mt-5 flex flex-col gap-3" onsubmit={onSubmit}>
			<label class="flex flex-col gap-1 text-[14px]">
				<span>Correo</span>
				<input
					type="email"
					bind:value={email}
					required
					autocomplete="username"
					class="min-h-11 rounded-[12px] border border-line bg-bg px-3"
				/>
			</label>
			<label class="flex flex-col gap-1 text-[14px]">
				<span>Contraseña</span>
				<input
					type="password"
					bind:value={password}
					required
					autocomplete="current-password"
					class="min-h-11 rounded-[12px] border border-line bg-bg px-3"
				/>
			</label>
			<Button type="submit" variant="primary">Entrar</Button>
		</form>

		{#if message}
			<p role="status" class="mt-3 text-[13px] text-ink-2">{message}</p>
		{/if}
	</div>
</div>
