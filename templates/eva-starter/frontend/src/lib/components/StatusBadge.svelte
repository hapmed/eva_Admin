<script lang="ts">
	import { CircleCheck, CircleHelp, CircleX, TriangleAlert } from '@lucide/svelte';

	type Status = 'active' | 'warning' | 'critical' | 'unknown';

	let { status, label }: { status: Status; label: string } = $props();

	const config = {
		active: { icon: CircleCheck, classes: 'text-success' },
		warning: { icon: TriangleAlert, classes: 'text-warning' },
		critical: { icon: CircleX, classes: 'text-danger' },
		unknown: { icon: CircleHelp, classes: 'text-ink-3' }
	} as const;

	const current = $derived(config[status]);
	const Icon = $derived(current.icon);
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full bg-surface-2 px-2.5 py-1 text-[13px] font-medium"
>
	<Icon size={14} class={current.classes} aria-hidden="true" />
	<span>{label}</span>
</span>
