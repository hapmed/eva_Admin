<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Eva = {
		id: string;
		code: string;
		name: string;
		status: string;
		versions: { id: string; version: string; status: string }[];
	};

	let evas = $state<Eva[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreate = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let form = $state({
		code: '',
		name: '',
		description: '',
		image_repo: '',
		container_port: 8000,
		healthcheck_path: '/healthz'
	});

	let versionFor = $state<Eva | null>(null);
	let versionOpen = $state(false);
	let versionForm = $state({ version: '', status: 'approved' });

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const rows = $derived(
		evas.map((eva) => ({
			...eva,
			versions_text: eva.versions.map((item) => item.version).join(', ') || '—'
		}))
	);

	async function load() {
		loading = true;
		error = null;
		try {
			evas = await api.get<Eva[]>('/evas');
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar el catálogo';
		} finally {
			loading = false;
		}
	}

	async function create() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<Eva>('/evas', form);
			evas = [...evas, { ...created, versions: created.versions ?? [] }];
			showCreate = false;
			form = {
				code: '',
				name: '',
				description: '',
				image_repo: '',
				container_port: 8000,
				healthcheck_path: '/healthz'
			};
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear la EVA';
		} finally {
			saving = false;
		}
	}

	function openVersion(eva: Eva) {
		versionFor = eva;
		versionForm = { version: '', status: 'approved' };
		versionOpen = true;
	}

	async function addVersion() {
		if (!versionFor) return;
		saving = true;
		formError = null;
		try {
			const created = await api.post<{ id: string; version: string; status: string }>(
				`/evas/${versionFor.id}/versions`,
				versionForm
			);
			const target = versionFor;
			evas = evas.map((item) =>
				item.id === target.id ? { ...item, versions: [...item.versions, created] } : item
			);
			versionOpen = false;
			versionFor = null;
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al añadir la versión';
		} finally {
			saving = false;
		}
	}

	onMount(load);
</script>

<PageHeader title="Catálogo EVA" subtitle="Aplicaciones EVA y versiones admitidas">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Nueva EVA</Button>
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
				{ key: 'code', label: 'Código' },
				{ key: 'name', label: 'Nombre' },
				{ key: 'status', label: 'Estado' },
				{ key: 'versions_text', label: 'Versiones' }
			]}
			{rows}
			emptyTitle="Catálogo vacío"
			emptyDescription="Registra la primera aplicación EVA con el botón «Nueva EVA»."
		>
			{#snippet actions(row)}
				<div class="flex justify-end">
					<Button variant="ghost" onclick={() => openVersion(row as Eva)}>Añadir versión</Button>
				</div>
			{/snippet}
		</DataTable>
	</div>
{/if}

<Modal bind:open={showCreate} title="Nueva aplicación EVA">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Código (identificador estable)</span>
			<input class={inputClass} bind:value={form.code} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Nombre</span>
			<input class={inputClass} bind:value={form.name} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Descripción</span>
			<input class={inputClass} bind:value={form.description} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Imagen Docker (repositorio, sin tag)</span>
			<input
				class={inputClass}
				bind:value={form.image_repo}
				placeholder="ghcr.io/hapmed/eva-mi-app"
			/>
		</label>
		<div class="grid grid-cols-2 gap-3">
			<label class="flex flex-col gap-1">
				<span>Puerto interno</span>
				<input type="number" class={inputClass} bind:value={form.container_port} />
			</label>
			<label class="flex flex-col gap-1">
				<span>Ruta de salud</span>
				<input class={inputClass} bind:value={form.healthcheck_path} placeholder="/healthz" />
			</label>
		</div>
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

<Modal
	bind:open={versionOpen}
	title={`Añadir versión${versionFor ? ' · ' + versionFor.code : ''}`}
	onclose={() => (versionFor = null)}
>
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Versión</span>
			<input class={inputClass} bind:value={versionForm.version} placeholder="1.0.0" />
		</label>
		<label class="flex flex-col gap-1">
			<span>Estado</span>
			<select class={inputClass} bind:value={versionForm.status}>
				<option value="approved">Aprobada</option>
				<option value="deprecated">Obsoleta</option>
				<option value="blocked">Bloqueada</option>
			</select>
		</label>
		{#if formError}
			<p class="text-[13px] text-danger" role="alert">{formError}</p>
		{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (versionOpen = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={addVersion}>
			{saving ? 'Guardando…' : 'Añadir'}
		</Button>
	{/snippet}
</Modal>
