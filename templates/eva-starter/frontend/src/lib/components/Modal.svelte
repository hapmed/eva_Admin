<script lang="ts">
	import { X } from '@lucide/svelte';
	import type { Snippet } from 'svelte';

	let {
		open = $bindable(false),
		title,
		onclose,
		children,
		footer
	}: {
		open?: boolean;
		title: string;
		onclose?: () => void;
		children: Snippet;
		footer?: Snippet;
	} = $props();

	function close() {
		open = false;
		onclose?.();
	}
</script>

{#if open}
	<div class="fixed inset-0 z-40 flex items-center justify-center p-4">
		<button class="absolute inset-0 bg-black/40" aria-label="Cerrar" onclick={close}></button>
		<div
			role="dialog"
			aria-modal="true"
			aria-label={title}
			class="relative z-10 w-full max-w-lg rounded-brand-lg border border-line bg-surface p-5 shadow-xl"
		>
			<div class="flex items-center justify-between">
				<h2 class="text-[17px] font-semibold">{title}</h2>
				<button
					class="inline-flex h-9 w-9 items-center justify-center rounded-[10px] hover:bg-surface-2"
					aria-label="Cerrar"
					onclick={close}
				>
					<X size={18} aria-hidden="true" />
				</button>
			</div>
			<div class="mt-4">{@render children()}</div>
			{#if footer}
				<div class="mt-5 flex justify-end gap-2">{@render footer()}</div>
			{/if}
		</div>
	</div>
{/if}
