<script lang="ts">
	import type { Snippet } from 'svelte';

	type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';

	let {
		variant = 'secondary',
		type = 'button',
		disabled = false,
		href,
		onclick,
		children
	}: {
		variant?: Variant;
		type?: 'button' | 'submit';
		disabled?: boolean;
		href?: string;
		onclick?: (event: MouseEvent) => void;
		children: Snippet;
	} = $props();

	const base =
		'inline-flex min-h-11 items-center justify-center gap-2 rounded-[12px] px-4 text-[15px] font-medium transition-colors';
	const variants: Record<Variant, string> = {
		primary: 'bg-accent text-white hover:opacity-90',
		secondary: 'bg-surface-2 text-ink hover:bg-line',
		ghost: 'bg-transparent text-ink hover:bg-surface-2',
		danger: 'bg-danger text-white hover:opacity-90'
	};
	const classes = $derived(
		`${base} ${variants[variant]} ${disabled ? 'pointer-events-none opacity-50' : ''}`
	);
</script>

{#if href}
	<a {href} class={classes}>{@render children()}</a>
{:else}
	<button {type} {disabled} {onclick} class={classes}>{@render children()}</button>
{/if}
