<script lang="ts">
	import { page } from '$app/state';
	import { navGroups } from '../nav';

	let { onNavigate }: { onNavigate?: () => void } = $props();

	function isActive(href: string): boolean {
		return href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href);
	}
</script>

<nav aria-label="Navegación principal" class="flex flex-col">
	{#each navGroups as group (group.label)}
		<p class="px-3 pt-4 pb-1 text-[11px] font-semibold tracking-wider text-ink-3 uppercase">
			{group.label}
		</p>
		<ul>
			{#each group.items as item (item.href)}
				{@const Icon = item.icon}
				{@const activeState = isActive(item.href)}
				<li>
					<a
						href={item.href}
						onclick={() => onNavigate?.()}
						aria-current={activeState ? 'page' : undefined}
						class="flex min-h-11 items-center gap-3 rounded-[12px] px-3 text-[15px] {activeState
							? 'bg-surface-2 font-medium text-ink'
							: 'text-ink-2 hover:bg-surface-2'}"
					>
						<Icon size={18} aria-hidden="true" />
						<span>{item.label}</span>
					</a>
				</li>
			{/each}
		</ul>
	{/each}
</nav>
