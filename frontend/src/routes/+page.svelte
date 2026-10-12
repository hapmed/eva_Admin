<script lang="ts">
	import { onMount } from 'svelte';
	import { Activity, Bell, Building2, Server } from '@lucide/svelte';
	import PageHeader from '../lib/components/PageHeader.svelte';
	import { api } from '../lib/api/client';

	type Alert = { key: string; type: string; severity: string; message: string; status: string };

	const cards = [
		{ label: 'Clientes activos', icon: Building2, value: '—' },
		{ label: 'Instalaciones', icon: Server, value: '—' },
		{ label: 'Alertas abiertas', icon: Bell, value: '—' },
		{ label: 'Salud global', icon: Activity, value: '—' }
	];

	let alerts = $state<Alert[]>([]);
	let alertCount = $state(0);

	const severityClass: Record<string, string> = {
		critical: 'text-danger',
		warning: 'text-warning',
		info: 'text-ink-2'
	};

	onMount(async () => {
		try {
			const all = await api.get<Alert[]>('/alerts');
			alerts = all.filter((alert) => alert.status === 'open');
			alertCount = alerts.length;
		} catch {
			alerts = [];
		}
	});
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
			<p class="mt-2 text-[28px] font-semibold">
				{card.label === 'Alertas abiertas' ? alertCount : card.value}
			</p>
		</div>
	{/each}
</section>

<section class="mt-8">
	<div class="mb-2 flex items-center justify-between">
		<h2 class="text-[17px] font-semibold">Notificaciones / Alertas</h2>
		<a href="/alertas" class="text-[14px] text-accent hover:underline">Ver todas →</a>
	</div>
	{#if alerts.length === 0}
		<p class="rounded-brand border border-line bg-surface-2 px-4 py-3 text-[14px] text-ink-2">
			No hay alertas abiertas.
		</p>
	{:else}
		<ul class="flex flex-col gap-2">
			{#each alerts as alert (alert.key)}
				<li
					class="flex items-center gap-3 rounded-brand border border-line bg-surface px-4 py-3 text-[14px]"
				>
					<Bell
						size={16}
						class={severityClass[alert.severity] ?? 'text-ink-2'}
						aria-hidden="true"
					/>
					<span class="flex-1">{alert.message}</span>
					<span class="text-[12px] text-ink-3">{alert.type}</span>
				</li>
			{/each}
		</ul>
	{/if}
</section>

<p class="mt-6 rounded-brand border border-line bg-surface-2 px-4 py-3 text-[14px] text-ink-2">
	Los indicadores de clientes/instalaciones/salud se conectarán a la API en siguientes iteraciones.
</p>
