<script lang="ts">
	import type { Snippet } from 'svelte';

	let { title, description, action }: { title: string; description?: string; action?: Snippet } =
		$props();
</script>

<div
	class="flex flex-col items-center justify-center gap-2 rounded-brand-lg border border-line bg-surface px-6 py-12 text-center"
>
	<p class="text-[17px] font-semibold">{title}</p>
	{#if description}
		<p class="max-w-md text-[15px] text-ink-2">{description}</p>
	{/if}
	{#if action}
		<div class="mt-2">{@render action()}</div>
	{/if}
</div>
