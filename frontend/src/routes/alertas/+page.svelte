<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Alertas" subtitle="Vencimientos, salud y backups" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="Las alertas configurables se implementan en la Fase 5."
	/>
</div>
