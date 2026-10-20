<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Client = { id: string; display_name: string; suggested_domain: string | null };
	type Eva = { id: string; name: string };
	type Installation = { id: string; client_id: string; eva_product_id: string };
	type Domain = { id: string; installation_id: string; fqdn: string; kind: string; status: string };

	let domains = $state<Domain[]>([]);
	let installations = $state<Installation[]>([]);
	let clients = $state<Client[]>([]);
	let evas = $state<Eva[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let availability = $state<boolean | null>(null);
	let form = $state({ installation_id: '', fqdn: '', kind: 'alias' });

	let editOpen = $state(false);
	let editFor = $state<Domain | null>(null);
	let editFqdn = $state('');
	let editError = $state<string | null>(null);
	let savingEdit = $state(false);

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const installationLabel = (id: string) => {
		const installation = installations.find((item) => item.id === id);
		if (!installation) return id;
		const client = clients.find((item) => item.id === installation.client_id)?.display_name ?? '—';
		const eva = evas.find((item) => item.id === installation.eva_product_id)?.name ?? '—';
		return `${client} · ${eva}`;
	};

	const rows = $derived(
		domains.map((domain) => ({
			...domain,
			installation_text: installationLabel(domain.installation_id)
		}))
	);

	async function load() {
		loading = true;
		error = null;
		try {
			[domains, installations, clients, evas] = await Promise.all([
				api.get<Domain[]>('/domains'),
				api.get<Installation[]>('/installations'),
				api.get<Client[]>('/clients'),
				api.get<Eva[]>('/evas')
			]);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar dominios';
		} finally {
			loading = false;
		}
	}

	async function check() {
		availability = null;
		if (!form.fqdn) return;
		try {
			const result = await api.get<{ available: boolean }>(
				`/domains/check?fqdn=${encodeURIComponent(form.fqdn)}`
			);
			availability = result.available;
		} catch {
			availability = null;
		}
	}

	async function create() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<Domain>('/domains', form);
			domains = [...domains, created];
			showCreate = false;
			form = { installation_id: '', fqdn: '', kind: 'alias' };
			availability = null;
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear el dominio';
		} finally {
			saving = false;
		}
	}

	async function remove(domain: Domain) {
		try {
			await api.delete(`/domains/${domain.id}`);
			domains = domains.filter((item) => item.id !== domain.id);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al eliminar';
		}
	}

	function applySuggestion() {
		const installation = installations.find((item) => item.id === form.installation_id);
		if (!installation) return;
		const client = clients.find((item) => item.id === installation.client_id);
		form.fqdn = client?.suggested_domain ?? '';
	}

	function openEdit(domain: Domain) {
		editFor = domain;
		editFqdn = domain.fqdn;
		editError = null;
		editOpen = true;
	}

	async function saveEdit() {
		if (!editFor) return;
		savingEdit = true;
		editError = null;
		try {
			const updated = await api.patch<Domain>(`/domains/${editFor.id}`, { fqdn: editFqdn });
			domains = domains.map((item) => (item.id === updated.id ? updated : item));
			editOpen = false;
			editFor = null;
		} catch (err) {
			editError = err instanceof ApiError ? err.message : 'Error al cambiar el dominio';
		} finally {
			savingEdit = false;
		}
	}

	onMount(load);
</script>

<PageHeader title="Dominios" subtitle="Dominios y subdominios por instalación">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Nuevo dominio</Button>
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
				{ key: 'fqdn', label: 'Dominio' },
				{ key: 'kind', label: 'Tipo' },
				{ key: 'status', label: 'Estado' },
				{ key: 'installation_text', label: 'Instalación' }
			]}
			{rows}
			emptyTitle="Sin dominios"
			emptyDescription="Registra el primer dominio con el botón «Nuevo dominio»."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					<Button variant="ghost" onclick={() => openEdit(row as Domain)}>Editar</Button>
					<Button variant="ghost" onclick={() => remove(row as Domain)}>Eliminar</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal bind:open={showCreate} title="Nuevo dominio">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Instalación</span>
			<select class={inputClass} bind:value={form.installation_id} onchange={applySuggestion}>
				<option value="">Selecciona…</option>
				{#each installations as installation (installation.id)}
					<option value={installation.id}>{installationLabel(installation.id)}</option>
				{/each}
			</select>
		</label>
		<label class="flex flex-col gap-1">
			<span>Dominio (FQDN)</span>
			<div class="flex gap-2">
				<input
					class={`${inputClass} flex-1`}
					bind:value={form.fqdn}
					placeholder="app.ejemplo.test"
				/>
				<Button variant="secondary" onclick={check}>Comprobar</Button>
			</div>
		</label>
		{#if availability !== null}
			<p class="text-[13px] {availability ? 'text-success' : 'text-danger'}">
				{availability ? 'Disponible' : 'No disponible (ya en uso)'}
			</p>
		{/if}
		<label class="flex flex-col gap-1">
			<span>Tipo</span>
			<select class={inputClass} bind:value={form.kind}>
				<option value="primary">Principal</option>
				<option value="alias">Alias</option>
			</select>
		</label>
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showCreate = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={create}
			>{saving ? 'Guardando…' : 'Crear'}</Button
		>
	{/snippet}
</Modal>

<Modal bind:open={editOpen} title="Cambiar dominio">
	<div class="flex flex-col gap-3 text-[14px]">
		<div class="rounded-[12px] bg-surface-2 px-3 py-2 text-[13px]">
			<p class="font-medium">{editFor?.fqdn ?? '—'}</p>
			<p class="text-ink-2">
				{editFor ? installationLabel(editFor.installation_id) : '—'}
			</p>
		</div>
		<label class="flex flex-col gap-1">
			<span>Nuevo dominio (FQDN)</span>
			<input class={inputClass} bind:value={editFqdn} placeholder="cliente.hapmed.qzz.io" />
			<span class="text-[12px] text-ink-3">
				Debe ser único. Se actualizará el DNS y la ruta del túnel.
			</span>
		</label>
		{#if editError}<p class="text-[13px] text-danger" role="alert">{editError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (editOpen = false)}>Cancelar</Button>
		<Button variant="primary" disabled={savingEdit} onclick={saveEdit}>
			{savingEdit ? 'Guardando…' : 'Guardar cambios'}
		</Button>
	{/snippet}
</Modal>
