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

	let databases = $state<Database[]>([]);
	let installations = $state<Installation[]>([]);
	let clients = $state<Client[]>([]);
	let evas = $state<Eva[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let form = $state({ installation_id: '', logical_name: '', host_ref: '' });

	let restoreFor = $state<Database | null>(null);
	let restoreOpen = $state(false);
	let backupRef = $state('');

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
		try {
			await api.post(`/databases/${database.id}/backup`, { idempotency_key: crypto.randomUUID() });
			await load();
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la copia de seguridad';
		}
	}

	function openRestore(database: Database) {
		restoreFor = database;
		backupRef = '';
		restoreOpen = true;
	}

	async function doRestore() {
		if (!restoreFor) return;
		saving = true;
		formError = null;
		try {
			await api.post(`/databases/${restoreFor.id}/restore`, {
				backup_ref: backupRef,
				idempotency_key: crypto.randomUUID()
			});
			restoreOpen = false;
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error en la restauración';
		} finally {
			saving = false;
		}
	}

	onMount(load);
</script>

<PageHeader title="Bases de datos" subtitle="Metadatos por instalación (sin credenciales)">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Registrar base de datos</Button>
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
				{ key: 'logical_name', label: 'Nombre lógico' },
				{ key: 'engine', label: 'Motor' },
				{ key: 'host_ref', label: 'Nodo' },
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
					<Button variant="ghost" onclick={() => openRestore(row as Database)}>Restaurar</Button>
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

<Modal bind:open={restoreOpen} title="Restaurar base de datos">
	<div class="flex flex-col gap-3 text-[14px]">
		<p class="text-ink-2">
			La restauración es una operación sensible. En modo simulado no realiza cambios reales.
		</p>
		<label class="flex flex-col gap-1">
			<span>Referencia de copia</span>
			<input class={inputClass} bind:value={backupRef} placeholder="backup-2026-10-11" />
		</label>
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (restoreOpen = false)}>Cancelar</Button>
		<Button variant="danger" disabled={saving} onclick={doRestore}
			>{saving ? 'Solicitando…' : 'Restaurar'}</Button
		>
	{/snippet}
</Modal>
