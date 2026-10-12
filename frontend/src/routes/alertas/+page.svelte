<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Alert = {
		key: string;
		type: string;
		severity: string;
		message: string;
		status: string;
	};

	let alerts = $state<Alert[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const rows = $derived(
		alerts.map((alert) => ({
			...alert,
			severity_text: alert.severity,
			status_text: alert.status
		}))
	);

	async function load() {
		loading = true;
		error = null;
		try {
			alerts = await api.get<Alert[]>('/alerts');
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar alertas';
		} finally {
			loading = false;
		}
	}

	async function act(alert: Alert, action: 'acknowledge' | 'resolve') {
		try {
			await api.post(`/alerts/${action}`, { key: alert.key });
			await load();
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la operación';
		}
	}

	onMount(load);
</script>

<PageHeader title="Alertas" subtitle="Vencimientos, salud y copias de seguridad" />

{#if loading}
	<p class="mt-6 text-[15px] text-ink-2">Cargando…</p>
{:else if error}
	<p class="mt-6 text-[15px] text-danger" role="alert">{error}</p>
{:else}
	<div class="mt-6">
		<DataTable
			columns={[
				{ key: 'severity_text', label: 'Severidad' },
				{ key: 'type', label: 'Tipo' },
				{ key: 'message', label: 'Descripción' },
				{ key: 'status_text', label: 'Estado' }
			]}
			{rows}
			emptyTitle="Sin alertas"
			emptyDescription="No hay alertas activas en este momento."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					<Button variant="ghost" onclick={() => act(row as Alert, 'acknowledge')}>
						Reconocer
					</Button>
					<Button variant="ghost" onclick={() => act(row as Alert, 'resolve')}>Resolver</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}
