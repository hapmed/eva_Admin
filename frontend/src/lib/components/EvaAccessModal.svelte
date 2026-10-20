<script lang="ts">
	import { ApiError, api } from '../api/client';
	import Button from './Button.svelte';
	import Modal from './Modal.svelte';

	type Installation = { id: string; container_name?: string };
	type Access = { email: string | null; password: string | null };

	let {
		installation,
		open = $bindable(false)
	}: { installation: Installation | null; open?: boolean } = $props();

	let email = $state<string | null>(null);
	let password = $state<string | null>(null);
	let loading = $state(false);
	let saving = $state(false);
	let error = $state<string | null>(null);
	let reveal = $state(false);
	let confirmReset = $state(false);
	let copied = $state<string | null>(null);

	$effect(() => {
		if (open && installation) load();
	});

	async function load() {
		if (!installation) return;
		loading = true;
		error = null;
		reveal = false;
		confirmReset = false;
		try {
			const access = await api.get<Access>(`/installations/${installation.id}/access`);
			email = access.email;
			password = access.password;
		} catch (err) {
			email = null;
			password = null;
			error = err instanceof ApiError ? err.message : 'Error al cargar el acceso';
		} finally {
			loading = false;
		}
	}

	async function createAccess() {
		if (!installation) return;
		saving = true;
		error = null;
		try {
			const access = await api.post<Access>(`/installations/${installation.id}/access`, {});
			email = access.email;
			password = access.password;
			reveal = true;
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al crear el acceso';
		} finally {
			saving = false;
		}
	}

	async function resetAccess() {
		if (!installation) return;
		saving = true;
		error = null;
		try {
			const access = await api.post<Access>(`/installations/${installation.id}/access/reset`, {});
			email = access.email;
			password = access.password;
			reveal = true;
			confirmReset = false;
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al regenerar la contraseña';
		} finally {
			saving = false;
		}
	}

	async function copy(value: string, field: string) {
		try {
			await navigator.clipboard.writeText(value);
			copied = field;
			setTimeout(() => {
				if (copied === field) copied = null;
			}, 2000);
		} catch {
			copied = null;
		}
	}
</script>

<Modal
	bind:open
	title={`Acceso a la EVA${installation?.container_name ? ' · ' + installation.container_name : ''}`}
>
	<div class="flex flex-col gap-4 text-[14px]">
		{#if error}
			<p class="text-[13px] text-danger" role="alert">{error}</p>
		{/if}

		{#if loading}
			<p class="text-ink-2">Cargando…</p>
		{:else if !email || !password}
			<p class="text-ink-2">
				Esta instalación todavía no tiene credenciales de administrador. Puedes generarlas ahora.
			</p>
			<div>
				<Button variant="primary" disabled={saving} onclick={createAccess}>
					{saving ? 'Creando…' : 'Crear acceso'}
				</Button>
			</div>
		{:else}
			<div class="rounded-[12px] bg-surface-2 p-3">
				<p class="text-[12px] text-ink-3">Correo</p>
				<div class="flex items-center justify-between gap-2">
					<p class="break-all font-medium">{email}</p>
					<Button variant="ghost" onclick={() => copy(email ?? '', 'email')}>
						{copied === 'email' ? 'Copiado' : 'Copiar'}
					</Button>
				</div>
			</div>

			<div class="rounded-[12px] bg-surface-2 p-3">
				<p class="text-[12px] text-ink-3">Contraseña</p>
				<div class="flex items-center justify-between gap-2">
					<p class="break-all font-mono font-medium">
						{reveal ? password : '••••••••••••'}
					</p>
					<div class="flex shrink-0 gap-1">
						<Button variant="ghost" onclick={() => (reveal = !reveal)}>
							{reveal ? 'Ocultar' : 'Mostrar'}
						</Button>
						<Button variant="ghost" onclick={() => copy(password ?? '', 'password')}>
							{copied === 'password' ? 'Copiado' : 'Copiar'}
						</Button>
					</div>
				</div>
			</div>

			<p class="text-[12px] text-warning">
				Comparte estas credenciales solo con el cliente. Si las regeneras, la contraseña anterior
				dejará de funcionar.
			</p>

			{#if confirmReset}
				<div class="rounded-[12px] border border-danger/30 p-3">
					<p class="text-[13px] text-danger">¿Seguro que quieres regenerar la contraseña?</p>
					<div class="mt-2 flex gap-2">
						<Button variant="danger" disabled={saving} onclick={resetAccess}>
							{saving ? 'Regenerando…' : 'Sí, regenerar'}
						</Button>
						<Button variant="secondary" onclick={() => (confirmReset = false)}>Cancelar</Button>
					</div>
				</div>
			{:else}
				<div>
					<Button variant="dangerGhost" onclick={() => (confirmReset = true)}>
						Regenerar contraseña
					</Button>
				</div>
			{/if}
		{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (open = false)}>Cerrar</Button>
	{/snippet}
</Modal>
