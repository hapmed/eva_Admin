<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Monitoreo" subtitle="Estado, healthchecks, logs y métricas" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="El monitoreo con el agente en modo simulado se implementa en la Fase 5. No se ejecutan operaciones Docker reales."
	/>
</div>
