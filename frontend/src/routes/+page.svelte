<script lang="ts">
	import { Activity, Bell, Building2, Server } from '@lucide/svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';

	const cards = [
		{ label: 'Clientes activos', icon: Building2, value: '—' },
		{ label: 'Instalaciones', icon: Server, value: '—' },
		{ label: 'Alertas abiertas', icon: Bell, value: '—' },
		{ label: 'Salud global', icon: Activity, value: '—' }
	];
</script>

<PageHeader title="Dashboard" subtitle="Resumen operativo de HAPMED" />

<section class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
	{#each cards as card (card.label)}
		{@const Icon = card.icon}
		<div class="rounded-brand border border-line bg-surface p-4">
			<div class="flex items-center gap-2 text-ink-2">
				<Icon size={16} aria-hidden="true" />
				<span class="text-[13px] font-medium">{card.label}</span>
			</div>
			<p class="mt-2 text-[28px] font-semibold">{card.value}</p>
		</div>
	{/each}
</section>

<p class="mt-6 rounded-brand border border-line bg-surface-2 px-4 py-3 text-[14px] text-ink-2">
	Los indicadores se conectarán a la API en las fases 3-5. Se muestra «—» para no presentar datos
	ficticios como reales.
</p>
