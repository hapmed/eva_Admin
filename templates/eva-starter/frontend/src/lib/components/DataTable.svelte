<script lang="ts">
	import type { Snippet } from 'svelte';
	import EmptyState from './EmptyState.svelte';

	let {
		columns,
		rows,
		actions,
		emptyTitle = 'Sin resultados',
		emptyDescription = 'No hay datos para mostrar.'
	}: {
		columns: { key: string; label: string }[];
		rows: Record<string, unknown>[];
		actions?: Snippet<[Record<string, unknown>]>;
		emptyTitle?: string;
		emptyDescription?: string;
	} = $props();

	function render(value: unknown): string {
		return value == null || value === '' ? '—' : String(value);
	}
</script>

{#if rows.length === 0}
	<EmptyState title={emptyTitle} description={emptyDescription} />
{:else}
	<div class="overflow-x-auto rounded-brand border border-line bg-surface">
		<table class="w-full border-collapse text-left text-[15px]">
			<caption class="sr-only">Tabla de datos</caption>
			<thead>
				<tr class="border-b border-line text-ink-2">
					{#each columns as column (column.key)}
						<th scope="col" class="px-4 py-3 font-medium">{column.label}</th>
					{/each}
					{#if actions}
						<th scope="col" class="px-4 py-3 text-right font-medium">Acciones</th>
					{/if}
				</tr>
			</thead>
			<tbody>
				{#each rows as row, index (index)}
					<tr class="border-b border-line last:border-0">
						{#each columns as column (column.key)}
							<td class="px-4 py-3">{render(row[column.key])}</td>
						{/each}
						{#if actions}
							<td class="px-4 py-3 text-right">{@render actions(row)}</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
