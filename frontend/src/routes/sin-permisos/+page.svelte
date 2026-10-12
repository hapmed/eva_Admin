<script lang="ts">
	import { ShieldX } from '@lucide/svelte';
	import Button from '#lib/components/Button.svelte';
</script>

<div
	class="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center gap-3 text-center"
>
	<ShieldX size={40} class="text-ink-3" aria-hidden="true" />
	<h1 class="text-[22px] font-semibold">Sin permisos</h1>
	<p class="text-[15px] text-ink-2">
		Tu cuenta no tiene acceso a esta sección. Contacta con un administrador.
	</p>
	<Button href="/" variant="secondary">Volver al dashboard</Button>
</div>
