<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Client = {
		id: string;
		legal_name: string;
		display_name: string;
		tax_id: string | null;
		status: string;
	};

	let clients = $state<Client[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let form = $state({ legal_name: '', display_name: '', tax_id: '', notes: '' });

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	async function load() {
		loading = true;
		error = null;
		try {
			clients = await api.get<Client[]>('/clients');
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar clientes';
		} finally {
			loading = false;
		}
	}

	async function create() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<Client>('/clients', form);
			clients = [...clients, created];
			showCreate = false;
			form = { legal_name: '', display_name: '', tax_id: '', notes: '' };
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear el cliente';
		} finally {
			saving = false;
		}
	}

	async function changeStatus(client: Client, action: 'suspend' | 'archive') {
		try {
			const updated = await api.post<Client>(`/clients/${client.id}/${action}`);
			clients = clients.map((item) => (item.id === updated.id ? updated : item));
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la operación';
		}
	}

	onMount(load);
</script>

<PageHeader title="Clientes" subtitle="Empresas y usuarios de cliente">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Nuevo cliente</Button>
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
				{ key: 'display_name', label: 'Nombre' },
				{ key: 'legal_name', label: 'Razón social' },
				{ key: 'status', label: 'Estado' }
			]}
			rows={clients}
			emptyTitle="Aún no hay clientes"
			emptyDescription="Crea el primer cliente con el botón «Nuevo cliente»."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					<Button variant="ghost" onclick={() => changeStatus(row as Client, 'suspend')}>
						Suspender
					</Button>
					<Button variant="ghost" onclick={() => changeStatus(row as Client, 'archive')}>
						Archivar
					</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal bind:open={showCreate} title="Nuevo cliente">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Nombre comercial</span>
			<input class={inputClass} bind:value={form.display_name} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Razón social</span>
			<input class={inputClass} bind:value={form.legal_name} />
		</label>
		<label class="flex flex-col gap-1">
			<span>NIF/CIF (opcional)</span>
			<input class={inputClass} bind:value={form.tax_id} />
		</label>
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
