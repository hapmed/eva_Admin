<script lang="ts">
	let {
		value,
		label,
		tone = 'accent'
	}: {
		value: number;
		label: string;
		tone?: 'accent' | 'warning' | 'danger' | 'muted';
	} = $props();

	const clamped = $derived(Math.min(Math.max(value, 0), 100));
	const color = $derived(
		tone === 'danger'
			? 'var(--color-danger)'
			: tone === 'warning'
				? 'var(--color-warning)'
				: tone === 'muted'
					? 'var(--color-ink-3)'
					: 'var(--color-accent)'
	);
</script>

<div
	class="h-2 w-full overflow-hidden rounded-full bg-surface-2"
	role="progressbar"
	aria-label={label}
	aria-valuemin="0"
	aria-valuemax="100"
	aria-valuenow={Math.round(clamped)}
>
	<div
		class="h-full rounded-full transition-[width] duration-500"
		style={`width: ${clamped}%; background-color: ${color}`}
	></div>
</div>
