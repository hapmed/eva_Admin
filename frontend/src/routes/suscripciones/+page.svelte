<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import { ApiError, api } from '../../lib/api/client';

	type Plan = {
		id: string;
		code: string;
		name: string;
		billing_period: string;
		price: string;
		currency: string;
	};
	type Client = { id: string; display_name: string };
	type Subscription = {
		id: string;
		client_id: string;
		plan_id: string;
		status: string;
		end_date: string;
		days_to_expiry: number;
		expiring_soon: boolean;
	};

	let plans = $state<Plan[]>([]);
	let clients = $state<Client[]>([]);
	let subscriptions = $state<Subscription[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showPlan = $state(false);
	let showSubscription = $state(false);
	let saving = $state(false);
	let formError = $state<string | null>(null);
	let planForm = $state({
		code: '',
		name: '',
		billing_period: 'monthly',
		price: '0.00',
		currency: 'USD'
	});
	let subForm = $state({ client_id: '', plan_id: '' });

	const inputClass = 'min-h-11 rounded-[12px] border border-line bg-bg px-3';

	const planName = (id: string) => plans.find((plan) => plan.id === id)?.name ?? id;
	const clientName = (id: string) => clients.find((client) => client.id === id)?.display_name ?? id;
	const dateOnly = (value: string) => value?.slice(0, 10) ?? '—';

	const subRows = $derived(
		subscriptions.map((sub) => ({
			...sub,
			client_text: clientName(sub.client_id),
			plan_text: planName(sub.plan_id),
			end_text: dateOnly(sub.end_date),
			expiry_text: `${sub.days_to_expiry} días`
		}))
	);

	async function load() {
		loading = true;
		error = null;
		try {
			[plans, clients, subscriptions] = await Promise.all([
				api.get<Plan[]>('/plans'),
				api.get<Client[]>('/clients'),
				api.get<Subscription[]>('/subscriptions')
			]);
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error al cargar datos';
		} finally {
			loading = false;
		}
	}

	async function createPlan() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<Plan>('/plans', planForm);
			plans = [...plans, created];
			showPlan = false;
			planForm = { code: '', name: '', billing_period: 'monthly', price: '0.00', currency: 'USD' };
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear el plan';
		} finally {
			saving = false;
		}
	}

	async function createSubscription() {
		saving = true;
		formError = null;
		try {
			const created = await api.post<Subscription>('/subscriptions', subForm);
			subscriptions = [...subscriptions, created];
			showSubscription = false;
			subForm = { client_id: '', plan_id: '' };
		} catch (err) {
			formError = err instanceof ApiError ? err.message : 'Error al crear la suscripción';
		} finally {
			saving = false;
		}
	}

	async function act(subscription: Subscription, action: 'renew' | 'cancel') {
		try {
			const updated = await api.post<Subscription>(
				`/subscriptions/${subscription.id}/${action}`,
				{}
			);
			subscriptions = subscriptions.map((item) => (item.id === updated.id ? updated : item));
		} catch (err) {
			error = err instanceof ApiError ? err.message : 'Error en la operación';
		}
	}

	onMount(load);
</script>

<PageHeader title="Suscripciones" subtitle="Planes, renovaciones y vencimientos">
	{#snippet actions()}
		<Button variant="secondary" onclick={() => (showPlan = true)}>Nuevo plan</Button>
		<Button variant="primary" onclick={() => (showSubscription = true)}>Nueva suscripción</Button>
	{/snippet}
</PageHeader>

{#if loading}
	<p class="mt-6 text-[15px] text-ink-2">Cargando…</p>
{:else if error}
	<p class="mt-6 text-[15px] text-danger" role="alert">{error}</p>
{:else}
	<section class="mt-6">
		<h2 class="mb-2 text-[17px] font-semibold">Planes</h2>
		<DataTable
			columns={[
				{ key: 'code', label: 'Código' },
				{ key: 'name', label: 'Nombre' },
				{ key: 'billing_period', label: 'Periodo' },
				{ key: 'price', label: 'Precio' },
				{ key: 'currency', label: 'Moneda' }
			]}
			rows={plans}
			emptyTitle="Sin planes"
			emptyDescription="Crea un plan para poder asignar suscripciones."
		/>
	</section>

	<section class="mt-8">
		<h2 class="mb-2 text-[17px] font-semibold">Suscripciones</h2>
		<DataTable
			columns={[
				{ key: 'client_text', label: 'Cliente' },
				{ key: 'plan_text', label: 'Plan' },
				{ key: 'status', label: 'Estado' },
				{ key: 'end_text', label: 'Vence' },
				{ key: 'expiry_text', label: 'Restante' }
			]}
			rows={subRows}
			emptyTitle="Sin suscripciones"
			emptyDescription="No hay suscripciones registradas."
		>
			{#snippet actions(row)}
				<div class="flex justify-end gap-1">
					<Button variant="ghost" onclick={() => act(row as Subscription, 'renew')}>Renovar</Button>
					<Button variant="ghost" onclick={() => act(row as Subscription, 'cancel')}
						>Cancelar</Button
					>
				</div>
			{/snippet}
		</DataTable>
	</section>
{/if}

<Modal bind:open={showPlan} title="Nuevo plan">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1"
			><span>Código</span><input class={inputClass} bind:value={planForm.code} /></label
		>
		<label class="flex flex-col gap-1"
			><span>Nombre</span><input class={inputClass} bind:value={planForm.name} /></label
		>
		<label class="flex flex-col gap-1">
			<span>Periodo</span>
			<select class={inputClass} bind:value={planForm.billing_period}>
				<option value="monthly">Mensual</option>
				<option value="quarterly">Trimestral</option>
				<option value="yearly">Anual</option>
			</select>
		</label>
		<label class="flex flex-col gap-1"
			><span>Precio</span><input class={inputClass} bind:value={planForm.price} /></label
		>
		<label class="flex flex-col gap-1"
			><span>Moneda</span><input
				class={inputClass}
				maxlength="3"
				bind:value={planForm.currency}
			/></label
		>
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showPlan = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={createPlan}
			>{saving ? 'Guardando…' : 'Crear'}</Button
		>
	{/snippet}
</Modal>

<Modal bind:open={showSubscription} title="Nueva suscripción">
	<div class="flex flex-col gap-3 text-[14px]">
		<label class="flex flex-col gap-1">
			<span>Cliente</span>
			<select class={inputClass} bind:value={subForm.client_id}>
				<option value="">Selecciona…</option>
				{#each clients as client (client.id)}
					<option value={client.id}>{client.display_name}</option>
				{/each}
			</select>
		</label>
		<label class="flex flex-col gap-1">
			<span>Plan</span>
			<select class={inputClass} bind:value={subForm.plan_id}>
				<option value="">Selecciona…</option>
				{#each plans as plan (plan.id)}
					<option value={plan.id}>{plan.name}</option>
				{/each}
			</select>
		</label>
		{#if formError}<p class="text-[13px] text-danger" role="alert">{formError}</p>{/if}
	</div>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showSubscription = false)}>Cancelar</Button>
		<Button variant="primary" disabled={saving} onclick={createSubscription}
			>{saving ? 'Guardando…' : 'Crear'}</Button
		>
	{/snippet}
</Modal>
