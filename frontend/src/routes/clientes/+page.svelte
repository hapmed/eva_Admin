<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Clientes" subtitle="Empresas y usuarios de cliente" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="La gestión de clientes y sus usuarios se implementa en la Fase 3. No se muestran datos ficticios."
	/>
</div>
