<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Auditoría" subtitle="Registro de operaciones administrativas" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="El registro de auditoría se implementa junto a las operaciones de las fases 3-5."
	/>
</div>
