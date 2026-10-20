<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '#lib/components/Button.svelte';
	import DataTable from '#lib/components/DataTable.svelte';
	import EmptyState from '#lib/components/EmptyState.svelte';
	import Modal from '#lib/components/Modal.svelte';
	import PageHeader from '#lib/components/PageHeader.svelte';
	import ProgressBar from '#lib/components/ProgressBar.svelte';
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
		start_date: string;
		end_date: string;
		days_to_expiry: number;
		days_total: number;
		days_elapsed: number;
		days_overdue: number;
		progress_percent: number;
		is_expired: boolean;
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

	const periodLabels: Record<string, string> = {
		monthly: 'Mensual',
		quarterly: 'Trimestral',
		yearly: 'Anual'
	};
	const periodLabel = (period: string) => periodLabels[period] ?? period;
	const planPeriod = (id: string) => {
		const plan = plans.find((item) => item.id === id);
		return plan ? periodLabel(plan.billing_period) : '—';
	};

	const planRows = $derived(
		plans.map((plan) => ({ ...plan, period_text: periodLabel(plan.billing_period) }))
	);

	const statusLabels: Record<string, string> = {
		draft: 'Borrador',
		active: 'Activa',
		grace: 'En gracia',
		suspended: 'Suspendida',
		expired: 'Vencida',
		cancelled: 'Cancelada'
	};

	const statusLabel = (status: string) => statusLabels[status] ?? status;

	function statusClass(status: string): string {
		if (status === 'active') return 'text-success';
		if (status === 'grace' || status === 'suspended') return 'text-warning';
		if (status === 'expired') return 'text-danger';
		return 'text-ink-2';
	}

	function daysText(days: number): string {
		return `${days} ${days === 1 ? 'día' : 'días'}`;
	}

	function remainingText(sub: Subscription): string {
		if (sub.status === 'cancelled') return 'Cancelada';
		if (sub.is_expired) {
			return sub.days_overdue === 0 ? 'Vencida hoy' : `Vencida hace ${daysText(sub.days_overdue)}`;
		}
		if (sub.days_to_expiry === 0) return 'Vence hoy';
		return `Quedan ${daysText(sub.days_to_expiry)}`;
	}

	function remainingClass(sub: Subscription): string {
		if (sub.status === 'cancelled') return 'text-ink-3';
		if (sub.is_expired) return 'text-danger';
		if (sub.expiring_soon) return 'text-warning';
		return 'text-ink-2';
	}

	function progressTone(sub: Subscription): 'accent' | 'warning' | 'danger' | 'muted' {
		if (sub.status === 'cancelled') return 'muted';
		if (sub.is_expired) return 'danger';
		if (sub.expiring_soon) return 'warning';
		return 'accent';
	}

	const summary = $derived([
		{
			label: 'Activas',
			value: subscriptions.filter((sub) => sub.status === 'active' || sub.status === 'grace').length
		},
		{
			label: 'Por vencer',
			value: subscriptions.filter((sub) => sub.expiring_soon).length
		},
		{
			label: 'Vencidas',
			value: subscriptions.filter((sub) => sub.is_expired && sub.status !== 'cancelled').length
		},
		{
			label: 'Canceladas',
			value: subscriptions.filter((sub) => sub.status === 'cancelled').length
		}
	]);

	const subRows = $derived(
		subscriptions.map((sub) => ({
			...sub,
			client_text: clientName(sub.client_id),
			plan_text: planName(sub.plan_id),
			status_text: statusLabel(sub.status),
			start_text: dateOnly(sub.start_date),
			end_text: dateOnly(sub.end_date),
			progress_text: `${Math.round(sub.progress_percent)} %`,
			expiry_text: remainingText(sub)
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
	<section class="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
		{#each summary as item (item.label)}
			<div class="rounded-brand border border-line bg-surface p-4">
				<p class="text-[13px] font-medium text-ink-2">{item.label}</p>
				<p class="mt-1 text-[26px] font-semibold">{item.value}</p>
			</div>
		{/each}
	</section>

	<section class="mt-8">
		<div class="mb-2 flex items-baseline justify-between gap-3">
			<h2 class="text-[17px] font-semibold">Tiempo de las suscripciones</h2>
			<span class="text-[12px] text-ink-3">Calculado al día de hoy</span>
		</div>
		{#if subscriptions.length === 0}
			<EmptyState
				title="Sin suscripciones"
				description="Crea una suscripción para ver su tiempo transcurrido y restante."
			/>
		{:else}
			<div class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
				{#each subscriptions as sub (sub.id)}
					<article class="flex flex-col rounded-brand border border-line bg-surface p-4">
						<div class="flex items-start justify-between gap-3">
							<div class="min-w-0">
								<p class="truncate text-[15px] font-semibold">{clientName(sub.client_id)}</p>
								<p class="truncate text-[13px] text-ink-2">
									{planName(sub.plan_id)} · {planPeriod(sub.plan_id)}
								</p>
							</div>
							<span class={`shrink-0 text-[12px] font-medium ${statusClass(sub.status)}`}>
								{statusLabel(sub.status)}
							</span>
						</div>

						<div class="mt-4">
							<div class="flex items-center justify-between gap-2 text-[12px]">
								<span class="text-ink-2">{sub.days_elapsed} de {sub.days_total} días</span>
								<span class={`font-medium ${remainingClass(sub)}`}>{remainingText(sub)}</span>
							</div>
							<div class="mt-1.5">
								<ProgressBar
									value={sub.progress_percent}
									tone={progressTone(sub)}
									label={`Progreso de la suscripción de ${clientName(sub.client_id)}`}
								/>
							</div>
							<p class="mt-1 text-right text-[12px] text-ink-3">
								{Math.round(sub.progress_percent)}% transcurrido
							</p>
						</div>

						<dl class="mt-3 grid grid-cols-2 gap-2 border-t border-line pt-3 text-[12px]">
							<div>
								<dt class="text-ink-3">Inicio</dt>
								<dd class="font-medium">{dateOnly(sub.start_date)}</dd>
							</div>
							<div>
								<dt class="text-ink-3">Vence</dt>
								<dd class="font-medium">{dateOnly(sub.end_date)}</dd>
							</div>
						</dl>
					</article>
				{/each}
			</div>
		{/if}
	</section>

	<section class="mt-8">
		<h2 class="mb-2 text-[17px] font-semibold">Planes</h2>
		<DataTable
			columns={[
				{ key: 'code', label: 'Código' },
				{ key: 'name', label: 'Nombre' },
				{ key: 'period_text', label: 'Periodo' },
				{ key: 'price', label: 'Precio' },
				{ key: 'currency', label: 'Moneda' }
			]}
			rows={planRows}
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
				{ key: 'status_text', label: 'Estado' },
				{ key: 'start_text', label: 'Inicio' },
				{ key: 'end_text', label: 'Vence' },
				{ key: 'progress_text', label: 'Progreso' },
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
