<script lang="ts">
	import { Moon, Sun } from '@lucide/svelte';

	let dark = $state(false);

	$effect(() => {
		if (typeof document === 'undefined') return;
		dark = document.documentElement.classList.contains('dark');
	});

	function toggle() {
		dark = !dark;
		document.documentElement.classList.toggle('dark', dark);
		try {
			localStorage.setItem('evas-theme', dark ? 'dark' : 'light');
		} catch (error) {
			/* almacenamiento no disponible */
		}
	}
</script>

<button
	type="button"
	onclick={toggle}
	aria-label={dark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
	class="inline-flex h-11 w-11 items-center justify-center rounded-[12px] text-ink hover:bg-surface-2"
>
	{#if dark}<Sun size={18} aria-hidden="true" />{:else}<Moon size={18} aria-hidden="true" />{/if}
</button>
