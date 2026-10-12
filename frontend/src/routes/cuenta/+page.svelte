<script lang="ts">
	import { onMount } from 'svelte';
	import { KeyRound, Plus } from '@lucide/svelte';
	import Button from '#lib/components/Button.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';
	import { registerPasskey, webAuthnSupported } from '../../lib/webauthn';
	import { sessionUser, type SessionUser } from '../../lib/stores/session';

	type Credential = { id: string; name: string; created_at: string; last_used_at: string | null };

	let credentials = $state<Credential[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let info = $state<string | null>(null);
	let canPasskey = $state(false);
	let addingPasskey = $state(false);

	let pwCurrent = $state('');
	let pwNew = $state('');
	let pwConfirm = $state('');
	let pwSaving = $state(false);
	let pwMsg = $state<string | null>(null);
	let pwErr = $state<string | null>(null);

	const inputClass = 'min-h-11 w-full rounded-[12px] border border-line bg-bg px-3';

	function fmt(value: string | null): string {
		return value ? value.slice(0, 10) : '—';
	}

	async function load() {
		loading = true;
		error = null;
		try {
			credentials = await api.get<Credential[]>('/auth/webauthn/credentials');
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar passkeys';
		} finally {
			loading = false;
		}
	}

	async function changePassword(event: SubmitEvent) {
		event.preventDefault();
		pwMsg = null;
		pwErr = null;
		if (pwNew !== pwConfirm) {
			pwErr = 'Las contraseñas no coinciden.';
			return;
		}
		pwSaving = true;
		try {
			await api.post('/auth/password/change', {
				current_password: pwCurrent,
				new_password: pwNew
			});
			pwMsg = 'Contraseña actualizada.';
			pwCurrent = '';
			pwNew = '';
			pwConfirm = '';
		} catch (err) {
			pwErr = err instanceof ApiError ? err.message : 'Error al cambiar la contraseña';
		} finally {
			pwSaving = false;
		}
	}

	async function addPasskey() {
		addingPasskey = true;
		info = null;
		error = null;
		try {
			const created = await registerPasskey();
			info = `Passkey «${created.name}» añadida.`;
			await load();
			const me = await api.get<SessionUser>('/auth/me');
			sessionUser.set(me);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo añadir la passkey';
		} finally {
			addingPasskey = false;
		}
	}

	async function removePasskey(cred: Credential) {
		try {
			await api.delete(`/auth/webauthn/credentials/${cred.id}`);
			credentials = credentials.filter((item) => item.id !== cred.id);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'No se pudo eliminar';
		}
	}

	onMount(() => {
		canPasskey = webAuthnSupported();
		load();
	});
</script>

<PageHeader title="Cuenta" subtitle="Contraseña y passkeys" />

{#if error}
	<p class="mt-4 text-[14px] text-danger" role="alert">{error}</p>
{/if}
{#if info}
	<p class="mt-4 text-[14px] text-success" role="status">{info}</p>
{/if}

<section class="mt-6 rounded-brand border border-line bg-surface p-5">
	<h2 class="text-[17px] font-semibold">Cambiar contraseña</h2>
	<form class="mt-4 grid max-w-md gap-3 text-[14px]" onsubmit={changePassword}>
		<label class="flex flex-col gap-1">
			<span>Contraseña actual</span>
			<input
				type="password"
				class={inputClass}
				bind:value={pwCurrent}
				autocomplete="current-password"
			/>
		</label>
		<label class="flex flex-col gap-1">
			<span>Nueva contraseña (mínimo 8)</span>
			<input type="password" class={inputClass} bind:value={pwNew} autocomplete="new-password" />
		</label>
		<label class="flex flex-col gap-1">
			<span>Repetir nueva contraseña</span>
			<input
				type="password"
				class={inputClass}
				bind:value={pwConfirm}
				autocomplete="new-password"
			/>
		</label>
		<div class="flex items-center gap-3">
			<Button type="submit" variant="primary" disabled={pwSaving}>
				{pwSaving ? 'Guardando…' : 'Guardar contraseña'}
			</Button>
			{#if pwMsg}<span class="text-[13px] text-success">{pwMsg}</span>{/if}
			{#if pwErr}<span class="text-[13px] text-danger">{pwErr}</span>{/if}
		</div>
	</form>
</section>

<section class="mt-6 rounded-brand border border-line bg-surface p-5">
	<div class="flex items-center justify-between">
		<h2 class="flex items-center gap-2 text-[17px] font-semibold">
			<KeyRound size={18} aria-hidden="true" /> Passkeys
		</h2>
		<Button variant="primary" disabled={!canPasskey || addingPasskey} onclick={addPasskey}>
			<Plus size={16} aria-hidden="true" />
			{addingPasskey ? 'Añadiendo…' : 'Añadir passkey'}
		</Button>
	</div>

	{#if !canPasskey}
		<p class="mt-3 text-[14px] text-ink-2">Este dispositivo o navegador no admite passkeys.</p>
	{:else if loading}
		<p class="mt-3 text-[14px] text-ink-2">Cargando…</p>
	{:else if credentials.length === 0}
		<p class="mt-3 text-[14px] text-ink-2">
			Aún no tienes passkeys. Añade una para entrar sin contraseña.
		</p>
	{:else}
		<ul class="mt-3 divide-y divide-line">
			{#each credentials as cred (cred.id)}
				<li class="flex items-center justify-between py-3">
					<div>
						<p class="font-medium">{cred.name}</p>
						<p class="text-[13px] text-ink-2">
							Añadida: {fmt(cred.created_at)} · Último uso: {fmt(cred.last_used_at)}
						</p>
					</div>
					<Button variant="ghost" onclick={() => removePasskey(cred)}>Eliminar</Button>
				</li>
			{/each}
		</ul>
	{/if}
</section>
