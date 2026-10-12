<script lang="ts">
	import { Activity, Boxes, CheckCircle2, Users } from '@lucide/svelte';
	import PageHeader from '../lib/components/PageHeader.svelte';

	const cards = [
		{ label: 'Registros', icon: Boxes, value: '—' },
		{ label: 'Usuarios', icon: Users, value: '—' },
		{ label: 'Operaciones hoy', icon: Activity, value: '—' },
		{ label: 'Estado', icon: CheckCircle2, value: '—' }
	];
</script>

<PageHeader title="Dashboard" subtitle="Resumen de la aplicación" />

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
	Conecta estos indicadores a tu API. Mientras no haya datos reales, se muestra «—».
</p>
