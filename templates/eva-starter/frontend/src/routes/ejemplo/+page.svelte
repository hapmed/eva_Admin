<script lang="ts">
	import Button from '../../lib/components/Button.svelte';
	import DataTable from '../../lib/components/DataTable.svelte';
	import Modal from '../../lib/components/Modal.svelte';
	import PageHeader from '../../lib/components/PageHeader.svelte';

	// DEMO de componentes. Sustituye el estado local por llamadas a tu API.
	type Item = { id: string; nombre: string; estado: string };

	let items = $state<Item[]>([]);
	let showCreate = $state(false);
	let form = $state({ nombre: '', estado: 'activo' });

	const inputClass = 'min-h-11 w-full rounded-[12px] border border-line bg-bg px-3';

	function create() {
		if (!form.nombre.trim()) return;
		items = [...items, { id: crypto.randomUUID(), nombre: form.nombre, estado: form.estado }];
		form = { nombre: '', estado: 'activo' };
		showCreate = false;
	}
</script>

<PageHeader title="Ejemplo" subtitle="Página de demostración de componentes">
	{#snippet actions()}
		<Button variant="primary" onclick={() => (showCreate = true)}>Nuevo</Button>
	{/snippet}
</PageHeader>

<div class="mt-6">
	<DataTable
		columns={[
			{ key: 'nombre', label: 'Nombre' },
			{ key: 'estado', label: 'Estado' }
		]}
		rows={items}
		emptyTitle="Sin registros"
		emptyDescription="Crea el primero con el botón «Nuevo»."
	/>
</div>

<p class="mt-4 text-[13px] text-ink-3">
	Nota: esta página es una demostración del diseño; reemplaza el estado local por tu API.
</p>

<Modal bind:open={showCreate} title="Nuevo registro">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Nombre</span>
			<input class={inputClass} bind:value={form.nombre} />
		</label>
		<label class="flex flex-col gap-1">
			<span>Estado</span>
			<select class={inputClass} bind:value={form.estado}>
				<option value="activo">Activo</option>
				<option value="inactivo">Inactivo</option>
			</select>
		</label>
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showCreate = false)}>Cancelar</Button>
		<Button variant="primary" onclick={create}>Crear</Button>
	{/snippet}
</Modal>
