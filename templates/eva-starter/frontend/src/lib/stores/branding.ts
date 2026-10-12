import { writable } from 'svelte/store';
import { api } from '../api/client';

// Nombre del cliente (branding). Se carga de /api/v1/config; por defecto HAPMED.
export const clientName = writable('HAPMED');

export async function loadBranding(): Promise<void> {
	try {
		const config = await api.get<{ client_name: string }>('/config');
		if (config.client_name) clientName.set(config.client_name);
	} catch {
		/* se mantiene el valor por defecto */
	}
}
