<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Eva = {
		id: string;
		name: string;
		versions: { version: string; status: string }[];
	};
	type Client = { id: string; display_name: string };
	type Installation = {
		id: string;
		client_id: string;
		eva_product_id: string;
		status: string;
		desired_version: string;
		installed_version: string | null;
		domains: string[];
	};

	let installations = $state<Installation[]>([]);
	let clients = $state<Client[]>([]);
	let evas = $state<Eva[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let form = $state({ client_id: '', eva_product_id: '', desired_version: '', primary_domain: '' });

	let upgradeFor = $state<Installation | null>(null);
	let upgradeOpen = $state(false);
	let upgradeVersion = $state('');

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const clientName = (id: string) => clients.find((c) => c.id === id)?.display_name ?? id;
	const evaName = (id: string) => evas.find((e) => e.id === id)?.name ?? id;
	const approvedVersions = (evaId: string) =>
		evas.find((e) => e.id === evaId)?.versions.filter((v) => v.status === 'approved') ?? [];

	const rows = $derived(
		installations.map((item) => ({
			...item,
			client_text: clientName(item.client_id),
			eva_text: evaName(item.eva_product_id),
			version_text: item.installed_version ?? '—',
			domains_text: item.domains.join(', ') || '—'
		}))
	);

	async function load() {
		loading = true;
		error = null;
		try {
			[clients, evas, installations] = await Promise.all([
				api.get<Client[]>('/clients'),
				api.get<Eva[]>('/evas'),
				api.get<Installation[]>('/installations')
			]);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar instalaciones';
		} finally {
			loading = false;
		}
	}

	async function create() {
		saving = true;
		formError = null;
		try {
			const payload: Record<string, unknown> = {
				client_id: form.client_id,
				eva_product_id: form.eva_product_id,
				desired_version: form.desired_version
			};
			if (form.primary_domain) payload.primary_domain = form.primary_domain;
			const created = await api.post<Installation>('/installations', payload);
			installations = [...installations, created];
			showCreate = false;
			form = { client_id: '', eva_product_id: '', desired_version: '', primary_domain: '' };
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear la instalación';
		} finally {
			saving = false;
		}
	}

	function openUpgrade(installation: Installation) {
		upgradeFor = installation;
		upgradeVersion = '';
		upgradeOpen = true;
	}

	async function doUpgrade() {
		if (!upgradeFor) return;
		saving = true;
		formError = null;
		try {
			await api.post(`/installations/${upgradeFor.id}/upgrade`, {
				target_version: upgradeVersion,
				idempotency_key: crypto.randomUUID()
			});
			upgradeOpen = false;
			await load();
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error en la actualización';
		} finally {
			saving = false;
		}
	}

	onMount(load);
</script>

<PageHeader title="Instalaciones" subtitle="Instancias por cliente">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Nueva instalación</Button>
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
				{ key: 'client_text', label: 'Cliente' },
				{ key: 'eva_text', label: 'EVA' },
				{ key: 'status', label: 'Estado' },
				{ key: 'version_text', label: 'Versión' },
				{ key: 'domains_text', label: 'Dominios' }
			]}
			{rows}
			emptyTitle="Sin instalaciones"
			emptyDescription="Crea la primera instalación con el botón «Nueva instalación»."
		>
			{#snippet actions(row)}
				<div class="flex justify-end">
					<Button variant="ghost" onclick={() => openUpgrade(row as Installation)}>
						Actualizar
					</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal bind:open={showCreate} title="Nueva instalación">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Cliente</span>
			<select class={inputClass} bind:value={form.client_id}>
				<option value="">Selecciona…</option>
				{#each clients as client (client.id)}<option value={client.id}>{client.display_name}</option
					>{/each}
			</select>
		</label>
		<label class="flex flex-col gap-1">
			<span>EVA</span>
			<select class={inputClass} bind:value={form.eva_product_id}>
				<option value="">Selecciona…</option>
				{#each evas as eva (eva.id)}<option value={eva.id}>{eva.name}</option>{/each}
			</select>
		</label>
		<label class="flex flex-col gap-1">
			<span>Versión deseada</span>
			<select class={inputClass} bind:value={form.desired_version}>
				<option value="">Selecciona…</option>
				{#each approvedVersions(form.eva_product_id) as version (version.version)}
					<option value={version.version}>{version.version}</option>
				{/each}
			</select>
		</label>
		<label class="flex flex-col gap-1">
			<span>Dominio principal (opcional)</span>
			<input
				class={inputClass}
				bind:value={form.primary_domain}
				placeholder="cliente.ejemplo.test"
			/>
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

<Modal
	bind:open={upgradeOpen}
	title={`Actualizar${upgradeFor ? ' · ' + evaName(upgradeFor.eva_product_id) : ''}`}
>
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Versión objetivo</span>
			<select class={inputClass} bind:value={upgradeVersion}>
				<option value="">Selecciona…</option>
				{#each upgradeFor ? approvedVersions(upgradeFor.eva_product_id) : [] as version (version.version)}
					<option value={version.version}>{version.version}</option>
				{/each}
			</select>
		</label>
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (upgradeOpen = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={doUpgrade}
			>{saving ? 'Aplicando…' : 'Actualizar'}</Button
		>
	{/snippet}
</Modal>
