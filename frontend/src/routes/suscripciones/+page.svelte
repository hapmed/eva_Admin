<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Suscripciones" subtitle="Planes, renovaciones y vencimientos" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="La gestión de planes y suscripciones se implementa en la Fase 3. No se procesan pagos en esta etapa."
	/>
</div>
