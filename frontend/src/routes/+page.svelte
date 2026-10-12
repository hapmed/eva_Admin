<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Activity,
		ArrowDown,
		ArrowUp,
		Bell,
		Building2,
		Server as ServerIcon
	} from '@lucide/svelte';
	import PageHeader from '../lib/components/PageHeader.svelte';
	import Gauge from '../lib/components/Gauge.svelte';
	import { api } from '../lib/api/client';

	type Alert = { key: string; type: string; severity: string; message: string; status: string };
	type System = {
		simulated: boolean;
		cpu_percent: number;
		cpu_count: number;
		mem_total: number;
		mem_used: number;
		mem_percent: number;
		disk_total: number;
		disk_used: number;
		disk_percent: number;
		load1: number;
		load5: number;
		load15: number;
		uptime_seconds: number;
		net_rx_bytes: number;
		net_tx_bytes: number;
		net_rx_rate: number;
		net_tx_rate: number;
	};

	const cards = [
		{ label: 'Clientes activos', icon: Building2, value: '—' },
		{ label: 'Instalaciones', icon: ServerIcon, value: '—' },
		{ label: 'Alertas abiertas', icon: Bell, value: '—' },
		{ label: 'Salud global', icon: Activity, value: '—' }
	];

	let alerts = $state<Alert[]>([]);
	let alertCount = $state(0);
	let system = $state<System | null>(null);

	const severityClass: Record<string, string> = {
		critical: 'text-danger',
		warning: 'text-warning',
		info: 'text-ink-2'
	};

	function gb(bytes: number): string {
		return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
	}

	function rate(bytesPerSecond: number): string {
		if (bytesPerSecond >= 1024 ** 2) return `${(bytesPerSecond / 1024 ** 2).toFixed(1)} MB/s`;
		if (bytesPerSecond >= 1024) return `${(bytesPerSecond / 1024).toFixed(0)} KB/s`;
		return `${Math.round(bytesPerSecond)} B/s`;
	}

	function uptime(seconds: number): string {
		const days = Math.floor(seconds / 86400);
		const hours = Math.floor((seconds % 86400) / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		if (days > 0) return `${days} d ${hours} h`;
		if (hours > 0) return `${hours} h ${minutes} min`;
		return `${minutes} min`;
	}

	function tone(percent: number): 'accent' | 'warning' | 'danger' {
		if (percent >= 90) return 'danger';
		if (percent >= 80) return 'warning';
		return 'accent';
	}

	onMount(async () => {
		try {
			const all = await api.get<Alert[]>('/alerts');
			alerts = all.filter((alert) => alert.status === 'open');
			alertCount = alerts.length;
		} catch {
			alerts = [];
		}
		try {
			system = await api.get<System>('/system');
		} catch {
			system = null;
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

<section class="mt-8 rounded-brand border border-line bg-surface p-5">
	<div class="mb-4 flex items-center justify-between">
		<h2 class="text-[17px] font-semibold">Estado del servidor</h2>
		{#if system?.simulated}
			<span class="text-[12px] text-ink-3">modo simulado</span>
		{/if}
	</div>

	{#if system && system.cpu_count > 0}
		<div class="grid grid-cols-3 gap-4 sm:max-w-md">
			<Gauge
				value={system.cpu_percent}
				label="CPU"
				detail={`${system.cpu_count} núcleos`}
				tone={tone(system.cpu_percent)}
			/>
			<Gauge
				value={system.mem_percent}
				label="RAM"
				detail={`${gb(system.mem_used)} / ${gb(system.mem_total)}`}
				tone={tone(system.mem_percent)}
			/>
			<Gauge
				value={system.disk_percent}
				label="Disco"
				detail={`${gb(system.disk_used)} / ${gb(system.disk_total)}`}
				tone={tone(system.disk_percent)}
			/>
		</div>

		<div class="mt-5 grid grid-cols-2 gap-3 text-[14px] sm:grid-cols-4">
			<div class="rounded-[12px] bg-surface-2 px-3 py-2">
				<p class="text-[12px] text-ink-2">Carga (1/5/15)</p>
				<p class="font-medium">
					{system.load1.toFixed(2)} / {system.load5.toFixed(2)} / {system.load15.toFixed(2)}
				</p>
			</div>
			<div class="rounded-[12px] bg-surface-2 px-3 py-2">
				<p class="text-[12px] text-ink-2">Encendido</p>
				<p class="font-medium">{uptime(system.uptime_seconds)}</p>
			</div>
			<div class="rounded-[12px] bg-surface-2 px-3 py-2">
				<p class="flex items-center gap-1 text-[12px] text-ink-2">
					<ArrowDown size={12} aria-hidden="true" /> Red entrante
				</p>
				<p class="font-medium">{rate(system.net_rx_rate)}</p>
			</div>
			<div class="rounded-[12px] bg-surface-2 px-3 py-2">
				<p class="flex items-center gap-1 text-[12px] text-ink-2">
					<ArrowUp size={12} aria-hidden="true" /> Red saliente
				</p>
				<p class="font-medium">{rate(system.net_tx_rate)}</p>
			</div>
		</div>
	{:else}
		<p class="text-[14px] text-ink-2">
			Sin métricas del servidor (agente en modo simulado o no disponible).
		</p>
	{/if}
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
