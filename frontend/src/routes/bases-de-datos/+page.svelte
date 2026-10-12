<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Client = { id: string; display_name: string };
	type Eva = { id: string; name: string };
	type Installation = { id: string; client_id: string; eva_product_id: string };
	type Database = {
		id: string;
		installation_id: string;
		engine: string;
		logical_name: string;
		host_ref: string;
		status: string;
		last_backup_at: string | null;
	};
	type Backup = {
		id: string;
		status: string;
		started_at: string | null;
		location_ref: string | null;
		size_bytes: number | null;
	};

	let databases = $state<Database[]>([]);
	let installations = $state<Installation[]>([]);
	let clients = $state<Client[]>([]);
	let evas = $state<Eva[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let info = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let form = $state({ installation_id: '', logical_name: '', host_ref: '' });

	let backupsFor = $state<Database | null>(null);
	let backupsOpen = $state(false);
	let backups = $state<Backup[]>([]);
	let backupsLoading = $state(false);
	let restoreConfirm = $state('');

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const installationLabel = (id: string) => {
		const installation = installations.find((item) => item.id === id);
		if (!installation) return id;
		const client = clients.find((item) => item.id === installation.client_id)?.display_name ?? '—';
		const eva = evas.find((item) => item.id === installation.eva_product_id)?.name ?? '—';
		return `${client} · ${eva}`;
	};

	const rows = $derived(
		databases.map((database) => ({
			...database,
			installation_text: installationLabel(database.installation_id),
			last_backup_text: database.last_backup_at ? database.last_backup_at.slice(0, 10) : 'Nunca'
		}))
	);

	function fmtSize(bytes: number | null): string {
		if (!bytes) return '—';
		return `${(bytes / 1024 ** 2).toFixed(2)} MB`;
	}

	async function load() {
		loading = true;
		error = null;
		try {
			[databases, installations, clients, evas] = await Promise.all([
				api.get<Database[]>('/databases'),
				api.get<Installation[]>('/installations'),
				api.get<Client[]>('/clients'),
				api.get<Eva[]>('/evas')
			]);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar bases de datos';
		} finally {
			loading = false;
		}
	}

	async function create() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<Database>('/databases', form);
			databases = [...databases, created];
			showCreate = false;
			form = { installation_id: '', logical_name: '', host_ref: '' };
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al registrar';
		} finally {
			saving = false;
		}
	}

	async function backup(database: Database) {
		info = null;
		error = null;
		try {
			await api.post(`/databases/${database.id}/backup`, { idempotency_key: crypto.randomUUID() });
			info = `Copia solicitada para ${database.logical_name}.`;
			await load();
			if (backupsFor?.id === database.id) await loadBackups(database);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la copia de seguridad';
		}
	}

	async function openBackups(database: Database) {
		backupsFor = database;
		backupsOpen = true;
		restoreConfirm = '';
		await loadBackups(database);
	}

	async function loadBackups(database: Database) {
		backupsLoading = true;
		try {
			backups = await api.get<Backup[]>(`/databases/${database.id}/backups`);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar copias';
		} finally {
			backupsLoading = false;
		}
	}

	async function restore(backup: Backup) {
		if (!backupsFor) return;
		saving = true;
		formError = null;
		try {
			await api.post(`/databases/${backupsFor.id}/restore`, {
				backup_ref: backup.id,
				confirm: restoreConfirm,
				idempotency_key: crypto.randomUUID()
			});
			backupsOpen = false;
			info = `Restauración solicitada para ${backupsFor.logical_name}.`;
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error en la restauración';
		} finally {
			saving = false;
		}
	}

	onMount(load);
</script>

<PageHeader title="Bases de datos" subtitle="Metadatos, copias de seguridad y restauración">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Registrar base de datos</Button>
	{/snippet}
</PageHeader>

{#if error}
	<p class="mt-4 text-[14px] text-danger" role="alert">{error}</p>
{/if}
{#if info}
	<p class="mt-4 text-[14px] text-success" role="status">{info}</p>
{/if}

{#if loading}
	<p class="mt-6 text-[15px] text-ink-2">Cargando…</p>
{:else}
	<div class="mt-6">
		<DataTable
			columns={[
				{ key: 'logical_name', label: 'Nombre lógico' },
				{ key: 'engine', label: 'Motor' },
				{ key: 'last_backup_text', label: 'Última copia' },
				{ key: 'installation_text', label: 'Instalación' }
			]}
			{rows}
			emptyTitle="Sin bases de datos"
			emptyDescription="Registra los metadatos de una base de datos asignada a una instalación."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					<Button variant="ghost" onclick={() => backup(row as Database)}>Backup</Button>
					<Button variant="ghost" onclick={() => openBackups(row as Database)}>Copias</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal bind:open={showCreate} title="Registrar base de datos">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Instalación</span>
			<select class={inputClass} bind:value={form.installation_id}>
				<option value="">Selecciona…</option>
				{#each installations as installation (installation.id)}
					<option value={installation.id}>{installationLabel(installation.id)}</option>
				{/each}
			</select>
		</label>
		<label class="flex flex-col gap-1">
			<span>Nombre lógico</span>
			<input class={inputClass} bind:value={form.logical_name} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Nodo (referencia)</span>
			<input class={inputClass} bind:value={form.host_ref} />
		</label>
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showCreate = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={create}
			>{saving ? 'Guardando…' : 'Registrar'}</Button
		>
	{/snippet}
</Modal>

<Modal bind:open={backupsOpen} title={`Copias · ${backupsFor?.logical_name ?? ''}`}>
	<div class="flex flex-col gap-3 text-[14px]">
		<Button variant="secondary" onclick={() => backupsFor && backup(backupsFor)}
			>Hacer copia ahora</Button
		>
		{#if backupsLoading}
			<p class="text-ink-2">Cargando…</p>
		{:else if backups.length === 0}
			<p class="text-ink-2">No hay copias todavía.</p>
		{:else}
			<ul class="divide-y divide-line">
				{#each backups as backup (backup.id)}
					<li class="flex items-center justify-between py-2">
						<div>
							<p class="font-medium">{backup.started_at?.slice(0, 19).replace('T', ' ') ?? '—'}</p>
							<p class="text-[12px] text-ink-2">{backup.status} · {fmtSize(backup.size_bytes)}</p>
						</div>
					</li>
				{/each}
			</ul>
			<div class="mt-2 rounded-[12px] bg-surface-2 p-3">
				<p class="mb-2 text-[13px] text-ink-2">
					Restaurar es sensible. Escribe el nombre de la base (<strong
						>{backupsFor?.logical_name}</strong
					>) y pulsa Restaurar.
				</p>
				<div class="flex gap-2">
					<input
						class={`${inputClass} flex-1`}
						bind:value={restoreConfirm}
						placeholder={backupsFor?.logical_name ?? ''}
					/>
					<Button
						variant="danger"
						disabled={saving || restoreConfirm !== backupsFor?.logical_name}
						onclick={() => backups[0] && restore(backups[0])}
					>
						Restaurar la más reciente
					</Button>
				</div>
			</div>
		{/if}
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (backupsOpen = false)}>Cerrar</Button>
	{/snippet}
</Modal>
