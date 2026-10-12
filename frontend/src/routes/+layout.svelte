<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { KeyRound, Menu, X } from '@lucide/svelte';
	import NavList from '../lib/components/NavList.svelte';
	import ThemeToggle from '../lib/components/ThemeToggle.svelte';
	import { loadSession, logout, sessionUser } from '../lib/stores/session';
	import { webAuthnSupported } from '../lib/webauthn';
	import '../app.css';

	let { children } = $props();
	let mobileOpen = $state(false);
	let canPasskey = $state(false);

	const showPasskeyTip = $derived(
		!!$sessionUser &&
			$sessionUser.has_passkeys === false &&
			canPasskey &&
			page.url.pathname !== '/cuenta' &&
			page.url.pathname !== '/login'
	);

	onMount(async () => {
		canPasskey = webAuthnSupported();
		await loadSession();
		// Respaldo del guard SSR: si no hay sesión, ir a login.
		if (!get(sessionUser) && page.url.pathname !== '/login') {
			await goto('/login');
		}
	});
</script>

<div class="min-h-dvh lg:grid lg:grid-cols-[264px_1fr]">
	<aside class="hidden border-r border-line bg-surface/70 backdrop-blur lg:flex lg:flex-col">
		<div class="flex h-16 items-center gap-2 px-5">
			<img src="/brand/logo-mark.png" alt="" class="h-8 w-8" />
			<span class="text-[17px] font-bold tracking-[0.18em]">HAPMED</span>
		</div>
		<div class="flex-1 overflow-y-auto px-3 pb-4">
			<NavList />
		</div>
	</aside>

	<div class="flex min-h-dvh flex-col">
		<header
			class="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-line bg-bg/80 px-4 backdrop-blur"
		>
			<button
				type="button"
				class="inline-flex h-11 w-11 items-center justify-center rounded-[12px] hover:bg-surface-2 lg:hidden"
				aria-label="Abrir menú"
				onclick={() => (mobileOpen = true)}
			>
				<Menu size={20} aria-hidden="true" />
			</button>
			<div class="flex items-center gap-2 lg:hidden">
				<img src="/brand/logo-mark.png" alt="" class="h-7 w-7" />
				<span class="text-[15px] font-bold tracking-[0.18em]">HAPMED</span>
			</div>
			<div class="ml-auto flex items-center gap-2">
				{#if $sessionUser}
					{#if $sessionUser.passkey_name}
						<span
							class="hidden items-center gap-1 rounded-full bg-surface-2 px-2.5 py-1 text-[12px] text-ink-2 sm:inline-flex"
						>
							<KeyRound size={13} aria-hidden="true" />
							{$sessionUser.passkey_name}
						</span>
					{/if}
					<span class="hidden text-[14px] text-ink-2 sm:inline">{$sessionUser.email}</span>
					<button
						type="button"
						class="inline-flex h-11 items-center rounded-[12px] px-3 text-[14px] text-ink hover:bg-surface-2"
						onclick={() => logout()}
					>
						Salir
					</button>
				{/if}
				<ThemeToggle />
			</div>
		</header>
		<main class="mx-auto w-full max-w-[1080px] flex-1 px-4 py-6 sm:px-6 lg:px-8">
			{#if showPasskeyTip}
				<a
					href="/cuenta"
					class="mb-4 flex items-center gap-3 rounded-brand border border-line bg-surface-2 px-4 py-3 text-[14px] text-ink hover:bg-line"
				>
					<KeyRound size={18} aria-hidden="true" />
					<span class="flex-1">
						Sugerencia: añade una <strong>passkey</strong> para entrar sin contraseña.
					</span>
					<span class="text-ink-2">Configurar →</span>
				</a>
			{/if}
			{@render children()}
		</main>
	</div>
</div>

{#if mobileOpen}
	<div class="fixed inset-0 z-30 lg:hidden">
		<button
			class="absolute inset-0 bg-black/40"
			aria-label="Cerrar menú"
			onclick={() => (mobileOpen = false)}
		></button>
		<div class="absolute inset-y-0 left-0 w-72 overflow-y-auto bg-surface p-3 shadow-xl">
			<div class="flex items-center justify-between px-2 py-2">
				<span class="text-[15px] font-bold tracking-[0.18em]">HAPMED</span>
				<button
					class="inline-flex h-10 w-10 items-center justify-center rounded-[12px] hover:bg-surface-2"
					aria-label="Cerrar menú"
					onclick={() => (mobileOpen = false)}
				>
					<X size={18} aria-hidden="true" />
				</button>
			</div>
			<NavList onNavigate={() => (mobileOpen = false)} />
		</div>
	</div>
{/if}
