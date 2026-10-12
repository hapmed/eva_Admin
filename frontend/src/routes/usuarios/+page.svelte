<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type User = {
		id: string;
		email: string;
		full_name: string;
		is_active: boolean;
		roles: string[];
	};
	type Role = { id: string; code: string; name: string };

	let users = $state<User[]>([]);
	let roles = $state<Role[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let form = $state({ email: '', full_name: '', password: '', roles: [] as string[] });

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const rows = $derived(
		users.map((user) => ({
			...user,
			roles_text: user.roles.join(', ') || '—',
			status_text: user.is_active ? 'Activo' : 'Inactivo'
		}))
	);

	async function load() {
		loading = true;
		error = null;
		try {
			[users, roles] = await Promise.all([api.get<User[]>('/users'), api.get<Role[]>('/roles')]);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar usuarios';
		} finally {
			loading = false;
		}
	}

	function toggleRole(code: string) {
		form.roles = form.roles.includes(code)
			? form.roles.filter((item) => item !== code)
			: [...form.roles, code];
	}

	async function create() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<User>('/users', form);
			users = [...users, created];
			showCreate = false;
			form = { email: '', full_name: '', password: '', roles: [] };
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear el usuario';
		} finally {
			saving = false;
		}
	}

	async function setActive(user: User, active: boolean) {
		try {
			const updated = await api.post<User>(
				`/users/${user.id}/${active ? 'reactivate' : 'deactivate'}`
			);
			users = users.map((item) => (item.id === updated.id ? updated : item));
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la operación';
		}
	}

	onMount(load);
</script>

<PageHeader title="Usuarios internos" subtitle="Equipo HAPMED, roles y permisos">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Nuevo usuario</Button>
	{/snippet}
</PageHeader>

{#if loading}
	<p class="mt-6 text-[15px] text-ink-2">Cargando…</p>
{:else if error}
	<p class="mt-6 text-[15px] text-danger" role="alert">{error}</p>
{:else}
	<div class="mt-6">
		<DataTable
			columns={[
				{ key: 'email', label: 'Correo' },
				{ key: 'full_name', label: 'Nombre' },
				{ key: 'roles_text', label: 'Roles' },
				{ key: 'status_text', label: 'Estado' }
			]}
			{rows}
			emptyTitle="Sin usuarios"
			emptyDescription="No hay usuarios internos registrados."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					{#if (row as User).is_active}
						<Button variant="ghost" onclick={() => setActive(row as User, false)}>
							Desactivar
						</Button>
					{:else}
						<Button variant="ghost" onclick={() => setActive(row as User, true)}>Reactivar</Button>
					{/if}
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal bind:open={showCreate} title="Nuevo usuario interno">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Correo</span>
			<input type="email" class={inputClass} bind:value={form.email} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Nombre</span>
			<input class={inputClass} bind:value={form.full_name} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Contraseña (mínimo 8 caracteres)</span>
			<input type="password" class={inputClass} bind:value={form.password} />
		</label>
		<fieldset class="flex flex-col gap-1">
			<legend class="mb-1">Roles</legend>
			{#each roles as role (role.id)}
				<label class="flex items-center gap-2">
					<input
						type="checkbox"
						checked={form.roles.includes(role.code)}
						onchange={() => toggleRole(role.code)}
					/>
					<span>{role.name}</span>
				</label>
			{/each}
		</fieldset>
		{#if formError}
			<p class="text-[13px] text-danger" role="alert">{formError}</p>
		{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showCreate = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={create}>
			{saving ? 'Guardando…' : 'Crear'}
		</Button>
	{/snippet}
</Modal>
