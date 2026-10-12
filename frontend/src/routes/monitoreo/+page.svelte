<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
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
	};
	type ServiceHealth = {
		service_name: string;
		status: string;
		health_status: string;
		last_checked_at: string | null;
	};

	let installations = $state<Installation[]>([]);
	let clients = $state<Client[]>([]);
	let evas = $state<Eva[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let detailFor = $state<Installation | null>(null);
	let detailOpen = $state(false);
	let health = $state<ServiceHealth[]>([]);
	let logs = $state<string[]>([]);
	let logsSimulated = $state(true);
	let metricsSimulated = $state(true);

	const clientName = (id: string) => clients.find((c) => c.id === id)?.display_name ?? id;
	const evaName = (id: string) => evas.find((e) => e.id === id)?.name ?? id;

	const rows = $derived(
		installations.map((item) => ({
			...item,
			client_text: clientName(item.client_id),
			eva_text: evaName(item.eva_product_id),
			version_text: item.installed_version ?? '—'
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
			error = err instanceof ApiError ? err.message : 'Error al cargar';
		} finally {
			loading = false;
		}
	}

	async function checkHealth(installation: Installation) {
		try {
			await api.post(`/installations/${installation.id}/health-check`);
			await load();
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la comprobación';
		}
	}

	async function openDetail(installation: Installation) {
		detailFor = installation;
		detailOpen = true;
		health = [];
		logs = [];
		try {
			const [h, l, m] = await Promise.all([
				api.get<{ services: ServiceHealth[] }>(`/installations/${installation.id}/health`),
				api.get<{ lines: string[]; simulated: boolean }>(`/installations/${installation.id}/logs`),
				api.get<{ samples: unknown[]; simulated: boolean }>(
					`/installations/${installation.id}/metrics`
				)
			]);
			health = h.services;
			logs = l.lines;
			logsSimulated = l.simulated;
			metricsSimulated = m.simulated;
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar el detalle';
		}
	}

	onMount(load);
</script>

<PageHeader title="Monitoreo" subtitle="Estado, healthchecks, logs y métricas" />

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
				{ key: 'version_text', label: 'Versión' }
			]}
			{rows}
			emptyTitle="Sin instalaciones"
			emptyDescription="No hay instalaciones que monitorizar."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					<Button variant="ghost" onclick={() => checkHealth(row as Installation)}>
						Comprobar salud
					</Button>
					<Button variant="ghost" onclick={() => openDetail(row as Installation)}>Detalle</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal
	bind:open={detailOpen}
	title={`Detalle${detailFor ? ' · ' + evaName(detailFor.eva_product_id) : ''}`}
>
	<div class="flex flex-col gap-4 text-[14px]">
		<section>
			<h3 class="mb-1 font-semibold">Servicios</h3>
			{#if health.length === 0}
				<p class="text-ink-2">Sin servicios registrados.</p>
			{:else}
				<ul class="flex flex-col gap-1">
					{#each health as service (service.service_name)}
						<li class="flex justify-between rounded-[10px] bg-surface-2 px-3 py-2">
							<span>{service.service_name}</span>
							<span class="text-ink-2">{service.health_status}</span>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
		<section>
			<h3 class="mb-1 font-semibold">Logs</h3>
			{#if logs.length === 0}
				<p class="text-ink-2">
					Sin líneas de registro{logsSimulated ? ' (modo simulado)' : ''}.
				</p>
			{:else}
				<pre class="max-h-40 overflow-auto rounded-[10px] bg-surface-2 p-3 text-[12px]">{logs.join(
						'\n'
					)}</pre>
			{/if}
		</section>
		<section>
			<h3 class="mb-1 font-semibold">Métricas</h3>
			<p class="text-ink-2">
				{metricsSimulated ? 'Sin métricas (modo simulado).' : 'Sin métricas disponibles.'}
			</p>
		</section>
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (detailOpen = false)}>Cerrar</Button>
	{/snippet}
</Modal>
