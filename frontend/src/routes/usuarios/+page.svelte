<script lang="ts">
	import EmptyState from '#lib/components/EmptyState.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
</script>

<PageHeader title="Usuarios internos" subtitle="Equipo HAPMED, roles y permisos" />

<div class="mt-6">
	<EmptyState
		title="Aún sin datos"
		description="La gestión de usuarios internos y roles se implementa en la Fase 3. No se muestran datos ficticios."
	/>
</div>
