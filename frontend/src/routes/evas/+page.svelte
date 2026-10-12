<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Catálogo EVA" subtitle="Aplicaciones EVA y versiones admitidas" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="El catálogo de aplicaciones EVA y sus versiones se implementa en la Fase 3. No se aceptan imágenes ni parámetros arbitrarios."
	/>
</div>
