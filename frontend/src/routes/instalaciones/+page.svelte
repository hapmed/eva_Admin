<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Instalaciones" subtitle="Instancias por cliente" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="La gestión lógica de instalaciones, servicios y configuración se implementa en la Fase 4."
	/>
</div>
