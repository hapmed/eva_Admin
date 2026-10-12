<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Dominios" subtitle="Dominios y subdominios por instalación" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="El registro de dominios y la detección de conflictos se implementan en la Fase 4."
	/>
</div>
