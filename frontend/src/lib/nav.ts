import type { Component } from 'svelte';
import {
	Activity,
	Bell,
	Boxes,
	Building2,
	CreditCard,
	Database,
	Globe,
	LayoutDashboard,
	ScrollText,
	Server,
	Users,
	UserCog
} from '@lucide/svelte';

export type NavItem = { href: string; label: string; icon: Component };
export type NavGroup = { label: string; items: NavItem[] };

export const navGroups: NavGroup[] = [
	{
		label: 'Operación',
		items: [
			{ href: '/', label: 'Dashboard', icon: LayoutDashboard },
			{ href: '/instalaciones', label: 'Instalaciones', icon: Server },
			{ href: '/dominios', label: 'Dominios', icon: Globe },
			{ href: '/bases-de-datos', label: 'Bases de datos', icon: Database },
			{ href: '/monitoreo', label: 'Monitoreo', icon: Activity },
			{ href: '/alertas', label: 'Alertas', icon: Bell }
		]
	},
	{
		label: 'Comercial',
		items: [
			{ href: '/clientes', label: 'Clientes', icon: Building2 },
			{ href: '/evas', label: 'Catálogo EVA', icon: Boxes },
			{ href: '/suscripciones', label: 'Suscripciones', icon: CreditCard }
		]
	},
	{
		label: 'Administración',
		items: [
			{ href: '/usuarios', label: 'Usuarios internos', icon: Users },
			{ href: '/auditoria', label: 'Auditoría', icon: ScrollText },
			{ href: '/cuenta', label: 'Cuenta', icon: UserCog }
		]
	}
];
