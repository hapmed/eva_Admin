<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import EmptyState from '#lib/components/EmptyState.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Client = { id: string; display_name: string };
	type Eva = { id: string; name: string };
	type Installation = {
		id: string;
		client_id: string;
		eva_product_id: string;
		status: string;
		installed_version: string | null;
		domains: string[];
		container_name: string;
	};
	type EvaUser = {
		id: string;
		email: string;
		full_name: string;
		role: string;
		is_active: boolean;
		created_at: string | null;
	};
	type Row = EvaUser & {
		key: string;
		installation_id: string;
		client_id: string;
		eva_product_id: string;
		client_text: string;
		eva_text: string;
		domain_text: string;
		status_text: string;
	};

	let clients = $state<Client[]>([]);
	let evas = $state<Eva[]>([]);
	let installations = $state<Installation[]>([]);
	let rows = $state<Row[]>([]);
	let loadErrors = $state<string[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let search = $state('');
	let clientFilter = $state('');
	let installationFilter = $state('');

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let createForm = $state({
		installation_id: '',
		email: '',
		full_name: '',
		password: '',
		role: 'consulta'
	});
	let createResult = $state<{ email: string; password: string } | null>(null);

	let resetFor = $state<Row | null>(null);
	let resetOpen = $state(false);
	let resetPassword = $state('');
	let resetError = $state<string | null>(null);
	let resetting = $state(false);
	let resetResult = $state<string | null>(null);

	let deleteFor = $state<Row | null>(null);
	let deleteOpen = $state(false);
	let deleteError = $state<string | null>(null);
	let deleting = $state(false);

	let notice = $state<string | null>(null);
	let copied = $state<string | null>(null);

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const clientName = (id: string) => clients.find((item) => item.id === id)?.display_name ?? id;
	const evaName = (id: string) => evas.find((item) => item.id === id)?.name ?? id;

	function installationLabel(installation: Installation) {
		const domain = installation.domains[0] ?? installation.container_name;
		return `${clientName(installation.client_id)} · ${evaName(installation.eva_product_id)} · ${domain}`;
	}

	const installationOptions = $derived(
		installations.filter((item) => !clientFilter || item.client_id === clientFilter)
	);

	const filteredRows = $derived(
		rows.filter((row) => {
			if (clientFilter && row.client_id !== clientFilter) return false;
			if (installationFilter && row.installation_id !== installationFilter) return false;
			if (search) {
				const text =
					`${row.email} ${row.full_name} ${row.client_text} ${row.eva_text} ${row.domain_text}`.toLowerCase();
				if (!text.includes(search.toLowerCase())) return false;
			}
			return true;
		})
	);

	async function load() {
		loading = true;
		error = null;
		loadErrors = [];
		try {
			[clients, evas, installations] = await Promise.all([
				api.get<Client[]>('/clients'),
				api.get<Eva[]>('/evas'),
				api.get<Installation[]>('/installations')
			]);

			const results = await Promise.all(
				installations.map(async (installation) => {
					try {
						const users = await api.get<EvaUser[]>(`/installations/${installation.id}/users`);
						return { installation, users, error: null };
					} catch (err) {
						const message = err instanceof ApiError ? err.message : 'Error al cargar';
						return { installation, users: [] as EvaUser[], error: message };
					}
				})
			);

			rows = results.flatMap(({ installation, users }) =>
				users.map((user) => ({
					...user,
					key: `${installation.id}:${user.id}`,
					installation_id: installation.id,
					client_id: installation.client_id,
					eva_product_id: installation.eva_product_id,
					client_text: clientName(installation.client_id),
					eva_text: evaName(installation.eva_product_id),
					domain_text: installation.domains.join(', ') || '—',
					status_text: user.is_active ? 'Activo' : 'Inactivo'
				}))
			);
			loadErrors = results
				.filter((result) => result.error)
				.map(
					(result) =>
						`${installationLabel(result.installation)}: ${result.error ?? 'error desconocido'}`
				);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar los usuarios de EVA';
		} finally {
			loading = false;
		}
	}

	function generatePassword(length = 12): string {
		const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
		const values = crypto.getRandomValues(new Uint32Array(length));
		return Array.from(values, (value) => chars[value % chars.length]).join('');
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

	function openEva(row: Row) {
		const domain = row.domain_text.split(',')[0]?.trim();
		if (domain && domain !== '—') {
			window.open(`https://${domain}`, '_blank', 'noopener,noreferrer');
		}
	}

	function openCreate() {
		createForm = {
			installation_id: installationFilter,
			email: '',
			full_name: '',
			password: generatePassword(),
			role: 'consulta'
		};
		createResult = null;
		formError = null;
		showCreate = true;
	}

	async function createUser() {
		formError = null;
		if (!createForm.installation_id) {
			formError = 'Selecciona una instalación';
			return;
		}
		saving = true;
		try {
			await api.post(`/installations/${createForm.installation_id}/users`, {
				email: createForm.email,
				full_name: createForm.full_name,
				password: createForm.password,
				role: createForm.role
			});
			createResult = { email: createForm.email, password: createForm.password };
			notice = `Usuario ${createForm.email} creado`;
			await load();
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear el usuario';
		} finally {
			saving = false;
		}
	}

	function openReset(row: Row) {
		resetFor = row;
		resetPassword = generatePassword();
		resetError = null;
		resetResult = null;
		resetOpen = true;
	}

	async function doReset() {
		if (!resetFor) return;
		resetting = true;
		resetError = null;
		try {
			await api.post(
				`/installations/${resetFor.installation_id}/users/${resetFor.id}/reset-password`,
				{ password: resetPassword }
			);
			resetResult = resetPassword;
		} catch (err) {
			resetError = err instanceof ApiError ? err.message : 'Error al restablecer la contraseña';
		} finally {
			resetting = false;
		}
	}

	function openDelete(row: Row) {
		deleteFor = row;
		deleteError = null;
		deleteOpen = true;
	}

	async function doDelete() {
		if (!deleteFor) return;
		deleting = true;
		deleteError = null;
		try {
			await api.delete(`/installations/${deleteFor.installation_id}/users/${deleteFor.id}`);
			notice = `Usuario ${deleteFor.email} eliminado`;
			deleteOpen = false;
			deleteFor = null;
			await load();
		} catch (err) {
			deleteError = err instanceof ApiError ? err.message : 'Error al eliminar el usuario';
		} finally {
			deleting = false;
		}
	}

	onMount(load);
</script>

<PageHeader title="Usuarios EVA" subtitle="Usuarios de las aplicaciones desplegadas por cliente">
	{#snippet actions()}
		<Button variant="primary" onclick={openCreate}>Nuevo usuario</Button>
	{/snippet}
</PageHeader>

{#if loading}
	<p class="mt-6 text-[15px] text-ink-2">Cargando…</p>
{:else if error}
	<p class="mt-6 text-[15px] text-danger" role="alert">{error}</p>
{:else}
	{#if notice}
		<p
			class="mt-4 rounded-brand border border-line bg-surface-2 px-4 py-3 text-[14px]"
			role="status"
		>
			{notice}
		</p>
	{/if}

	{#if loadErrors.length > 0}
		<div
			class="mt-4 rounded-brand border border-line bg-surface-2 px-4 py-3 text-[13px] text-warning"
		>
			<p class="font-medium">No se pudieron leer usuarios de:</p>
			<ul class="mt-1 list-disc pl-5">
				{#each loadErrors as item (item)}
					<li>{item}</li>
				{/each}
			</ul>
		</div>
	{/if}

	<div class="mt-6 flex flex-col gap-3 lg:flex-row">
		<input class={inputClass} placeholder="Buscar correo, nombre, cliente…" bind:value={search} />
		<select class={inputClass} bind:value={clientFilter} onchange={() => (installationFilter = '')}>
			<option value="">Todos los clientes</option>
			{#each clients as client (client.id)}
				<option value={client.id}>{client.display_name}</option>
			{/each}
		</select>
		<select class={inputClass} bind:value={installationFilter}>
			<option value="">Todas las instalaciones</option>
			{#each installationOptions as installation (installation.id)}
				<option value={installation.id}>{installationLabel(installation)}</option>
			{/each}
		</select>
	</div>

	{#if installations.length === 0}
		<div class="mt-6">
			<EmptyState
				title="Sin instalaciones"
				description="Crea una instalación para poder administrar los usuarios de su EVA."
			/>
		</div>
	{:else}
		<div class="mt-6">
			<DataTable
				columns={[
					{ key: 'client_text', label: 'Cliente' },
					{ key: 'eva_text', label: 'EVA' },
					{ key: 'domain_text', label: 'Dominio' },
					{ key: 'email', label: 'Correo' },
					{ key: 'full_name', label: 'Nombre' },
					{ key: 'role', label: 'Rol' },
					{ key: 'status_text', label: 'Estado' }
				]}
				rows={filteredRows}
				emptyTitle="Sin usuarios"
				emptyDescription="Crea el primer usuario con el botón «Nuevo usuario»."
			>
				{#snippet actions(row)}
					<div class="flex justify-end gap-1">
						<Button variant="ghost" onclick={() => openEva(row as Row)}>Abrir EVA</Button>
						<Button variant="ghost" onclick={() => openReset(row as Row)}>Restablecer</Button>
						<Button variant="dangerGhost" onclick={() => openDelete(row as Row)}>Eliminar</Button>
					</div>
				{/snippet}
			</DataTable>
		</div>
	{/if}
{/if}

<Modal bind:open={showCreate} title="Nuevo usuario de EVA">
	{#if createResult}
		<div class="flex flex-col gap-3 text-[14px]">
			<p class="text-success">Usuario creado. Comparte estas credenciales con el cliente.</p>
			<div class="rounded-[12px] bg-surface-2 p-3">
				<p class="text-[12px] text-ink-3">Correo</p>
				<div class="flex items-center justify-between gap-2">
					<p class="break-all font-medium">{createResult.email}</p>
					<Button variant="ghost" onclick={() => copy(createResult?.email ?? '', 'new-email')}>
						{copied === 'new-email' ? 'Copiado' : 'Copiar'}
					</Button>
				</div>
			</div>
			<div class="rounded-[12px] bg-surface-2 p-3">
				<p class="text-[12px] text-ink-3">Contraseña</p>
				<div class="flex items-center justify-between gap-2">
					<p class="break-all font-mono font-medium">{createResult.password}</p>
					<Button
						variant="ghost"
						onclick={() => copy(createResult?.password ?? '', 'new-password')}
					>
						{copied === 'new-password' ? 'Copiado' : 'Copiar'}
					</Button>
				</div>
			</div>
		</div>
	{:else}
		<div class="flex flex-col gap-3 text-[14px]">
			<label class="flex flex-col gap-1">
				<span>Instalación</span>
				<select class={inputClass} bind:value={createForm.installation_id}>
					<option value="">Selecciona…</option>
					{#each installations as installation (installation.id)}
						<option value={installation.id}>{installationLabel(installation)}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col gap-1">
				<span>Correo</span>
				<input class={inputClass} type="email" bind:value={createForm.email} />
			</label>
			<label class="flex flex-col gap-1">
				<span>Nombre</span>
				<input class={inputClass} bind:value={createForm.full_name} />
			</label>
			<label class="flex flex-col gap-1">
				<span>Contraseña</span>
				<div class="flex gap-2">
					<input class={`${inputClass} flex-1`} bind:value={createForm.password} />
					<Button variant="secondary" onclick={() => (createForm.password = generatePassword())}>
						Generar
					</Button>
				</div>
			</label>
			<label class="flex flex-col gap-1">
				<span>Rol</span>
				<input
					class={inputClass}
					bind:value={createForm.role}
					placeholder="admin / ventas / consulta"
				/>
			</label>
			{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
		</div>
	{/if}
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showCreate = false)}>Cerrar</Button>
		{#if !createResult}
			<Button variant="primary" disabled={saving} onclick={createUser}>
				{saving ? 'Creando…' : 'Crear usuario'}
			</Button>
		{/if}
	{/snippet}
</Modal>

<Modal bind:open={resetOpen} title="Restablecer contraseña">
	{#if resetFor}
		<div class="flex flex-col gap-3 text-[14px]">
			<p class="text-ink-2">{resetFor.email}</p>
			{#if resetResult}
				<p class="text-success">Contraseña actualizada. Compártela con el cliente.</p>
				<div class="rounded-[12px] bg-surface-2 p-3">
					<div class="flex items-center justify-between gap-2">
						<p class="break-all font-mono font-medium">{resetResult}</p>
						<Button variant="ghost" onclick={() => copy(resetResult ?? '', 'reset-password')}>
							{copied === 'reset-password' ? 'Copiado' : 'Copiar'}
						</Button>
					</div>
				</div>
			{:else}
				<label class="flex flex-col gap-1">
					<span>Nueva contraseña</span>
					<div class="flex gap-2">
						<input class={`${inputClass} flex-1`} bind:value={resetPassword} />
						<Button variant="secondary" onclick={() => (resetPassword = generatePassword())}>
							Generar
						</Button>
					</div>
				</label>
				{#if resetError}<p class="text-[13px] text-danger" role="alert">{resetError}</p>{/if}
			{/if}
		</div>
	{/if}
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (resetOpen = false)}>Cerrar</Button>
		{#if !resetResult}
			<Button variant="primary" disabled={resetting} onclick={doReset}>
				{resetting ? 'Guardando…' : 'Restablecer'}
			</Button>
		{/if}
	{/snippet}
</Modal>

<Modal bind:open={deleteOpen} title="Eliminar usuario">
	{#if deleteFor}
		<div class="flex flex-col gap-3 text-[14px]">
			<p>
				¿Eliminar el usuario <strong>{deleteFor.email}</strong> de
				<strong>{deleteFor.eva_text}</strong>?
			</p>
			<p class="text-[13px] text-danger">Esta acción no se puede deshacer.</p>
			{#if deleteError}<p class="text-[13px] text-danger" role="alert">{deleteError}</p>{/if}
		</div>
	{/if}
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (deleteOpen = false)}>Cancelar</Button>
		<Button variant="danger" disabled={deleting} onclick={doDelete}>
			{deleting ? 'Eliminando…' : 'Eliminar'}
		</Button>
	{/snippet}
</Modal>
