<script lang="ts">
	let {
		value,
		label,
		detail,
		tone = 'accent'
	}: {
		value: number;
		label: string;
		detail?: string;
		tone?: 'accent' | 'warning' | 'danger';
	} = $props();

	const radius = 26;
	const circumference = 2 * Math.PI * radius;
	const clamped = $derived(Math.min(Math.max(value, 0), 100));
	const dash = $derived(circumference * (1 - clamped / 100));
	const color = $derived(
		tone === 'danger'
			? 'var(--color-danger)'
			: tone === 'warning'
				? 'var(--color-warning)'
				: 'var(--color-accent)'
	);
</script>

<div class="flex flex-col items-center gap-1">
	<div class="relative h-16 w-16">
		<svg viewBox="0 0 64 64" class="h-16 w-16 -rotate-90">
			<circle cx="32" cy="32" r={radius} fill="none" stroke="var(--color-line)" stroke-width="6" />
			<circle
				cx="32"
				cy="32"
				r={radius}
				fill="none"
				stroke={color}
				stroke-width="6"
				stroke-linecap="round"
				stroke-dasharray={circumference}
				stroke-dashoffset={dash}
			/>
		</svg>
		<span class="absolute inset-0 flex items-center justify-center text-[13px] font-semibold">
			{Math.round(value)}%
		</span>
	</div>
	<span class="text-[12px] font-medium text-ink-2">{label}</span>
	{#if detail}<span class="text-[11px] text-ink-3">{detail}</span>{/if}
</div>
