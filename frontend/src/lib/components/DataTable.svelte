<script lang="ts">
	import EmptyState from './EmptyState.svelte';

	let {
		columns,
		rows,
		emptyTitle = 'Sin resultados',
		emptyDescription = 'No hay datos para mostrar.'
	}: {
		columns: { key: string; label: string }[];
		rows: Record<string, unknown>[];
		emptyTitle?: string;
		emptyDescription?: string;
	} = $props();

	function render(value: unknown): string {
		return value == null ? '—' : String(value);
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
				</tr>
			</thead>
			<tbody>
				{#each rows as row, index (index)}
					<tr class="border-b border-line last:border-0">
						{#each columns as column (column.key)}
							<td class="px-4 py-3">{render(row[column.key])}</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
