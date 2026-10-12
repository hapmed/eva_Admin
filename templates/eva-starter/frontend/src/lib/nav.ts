import type { Component } from 'svelte';
import { Boxes, LayoutDashboard } from '@lucide/svelte';

export type NavItem = { href: string; label: string; icon: Component };
export type NavGroup = { label: string; items: NavItem[] };

// Personaliza los módulos de tu EVA aquí.
export const navGroups: NavGroup[] = [
	{
		label: 'General',
		items: [
			{ href: '/', label: 'Dashboard', icon: LayoutDashboard },
			{ href: '/ejemplo', label: 'Ejemplo', icon: Boxes }
		]
	}
];
