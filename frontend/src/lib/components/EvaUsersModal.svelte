<script lang="ts">
	import { api, ApiError } from '../api/client';
	import Button from './Button.svelte';
	import Modal from './Modal.svelte';

	type Installation = { id: string; container_name?: string };
	type EvaUser = { id: string; email: string; full_name: string; role: string; is_active: boolean };

	let {
		installation,
		open = $bindable(false)
	}: { installation: Installation | null; open?: boolean } = $props();

	let users = $state<EvaUser[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let saving = $state(false);
	let form = $state({ email: '', password: '', full_name: '', role: 'user' });
	let resetFor = $state<EvaUser | null>(null);
	let resetPassword = $state('');

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	$effect(() => {
		if (open && installation) load();
	});

	async function load() {
		if (!installation) return;
		loading = true;
		error = null;
		try {
			users = await api.get<EvaUser[]>(`/installations/${installation.id}/users`);
		} catch (err) {
			users = [];
			error = err instanceof ApiError ? err.message : 'Error al cargar usuarios';
		} finally {
			loading = false;
		}
	}

	async function create() {
		if (!installation) return;
		saving = true;
		error = null;
		try {
			await api.post(`/installations/${installation.id}/users`, form);
			form = { email: '', password: '', full_name: '', role: 'user' };
			await load();
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al crear el usuario';
		} finally {
			saving = false;
		}
	}

	async function doReset() {
		if (!installation || !resetFor) return;
		saving = true;
		error = null;
		try {
			await api.post(`/installations/${installation.id}/users/${resetFor.id}/reset-password`, {
				password: resetPassword
			});
			resetFor = null;
			resetPassword = '';
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al restablecer';
		} finally {
			saving = false;
		}
	}

	async function remove(user: EvaUser) {
		if (!installation) return;
		try {
			await api.delete(`/installations/${installation.id}/users/${user.id}`);
			users = users.filter((item) => item.id !== user.id);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al eliminar';
		}
	}
</script>

<Modal
	bind:open
	title={`Usuarios de la EVA${installation ? ' · ' + installation.container_name : ''}`}
>
	<div class="flex flex-col gap-4 text-[14px]">
		{#if error}
			<p class="text-[13px] text-danger" role="alert">{error}</p>
		{/if}

		<section>
			<h3 class="mb-2 font-semibold">Usuarios</h3>
			{#if loading}
				<p class="text-ink-2">Cargando…</p>
			{:else if users.length === 0}
				<p class="text-ink-2">Sin usuarios (o la EVA aún no tiene esquema).</p>
			{:else}
				<ul class="divide-y divide-line">
					{#each users as user (user.id)}
						<li class="flex items-center justify-between gap-2 py-2">
							<div>
								<p class="font-medium">{user.email}</p>
								<p class="text-[12px] text-ink-2">
									{user.full_name || '—'} · {user.role || '—'} · {user.is_active
										? 'activo'
										: 'inactivo'}
								</p>
							</div>
							<div class="flex gap-1">
								<Button variant="ghost" onclick={() => (resetFor = user)}>Restablecer</Button>
								<Button variant="ghost" onclick={() => remove(user)}>Eliminar</Button>
							</div>
						</li>
					{/each}
				</ul>
			{/if}
		</section>

		{#if resetFor}
			<section class="rounded-[12px] bg-surface-2 p-3">
				<p class="mb-2 text-[13px] text-ink-2">Nueva contraseña para {resetFor.email}</p>
				<div class="flex gap-2">
					<input type="password" class={`${inputClass} flex-1`} bind:value={resetPassword} />
					<Button variant="primary" disabled={saving || resetPassword.length < 8} onclick={doReset}>
						Guardar
					</Button>
					<Button variant="secondary" onclick={() => (resetFor = null)}>Cancelar</Button>
				</div>
			</section>
		{/if}

		<section class="rounded-[12px] bg-surface-2 p-3">
			<h3 class="mb-2 font-semibold">Añadir usuario</h3>
			<div class="grid gap-2 sm:grid-cols-2">
				<input class={inputClass} placeholder="Correo" bind:value={form.email} />
				<input class={inputClass} placeholder="Nombre" bind:value={form.full_name} />
				<input
					type="password"
					class={inputClass}
					placeholder="Contraseña (mín. 8)"
					bind:value={form.password}
				/>
				<input class={inputClass} placeholder="Rol" bind:value={form.role} />
			</div>
			<div class="mt-2 flex justify-end">
				<Button variant="primary" disabled={saving} onclick={create}>Crear</Button>
			</div>
		</section>
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (open = false)}>Cerrar</Button>
	{/snippet}
</Modal>
