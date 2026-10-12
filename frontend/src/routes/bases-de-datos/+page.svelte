<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Bases de datos" subtitle="Metadatos por instalación (sin credenciales)" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="Los metadatos de bases de datos (motor, host, estado, última copia) se implementan en la Fase 4. Nunca se muestran credenciales."
	/>
</div>
