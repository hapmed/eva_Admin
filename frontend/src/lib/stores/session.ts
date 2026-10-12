import { writable } from 'svelte/store';
import { ApiError, api } from '../api/client';

export type SessionUser = {
	id: string;
	email: string;
	full_name: string;
	roles: string[];
	permissions: string[];
};

export const sessionUser = writable<SessionUser | null>(null);

export function can(user: SessionUser | null, permission: string): boolean {
	return user?.permissions.includes(permission) ?? false;
}

export async function login(email: string, password: string): Promise<string | null> {
	try {
		const user = await api.post<SessionUser>('/auth/login', { email, password });
		sessionUser.set(user);
		return null;
	} catch (error) {
		return error instanceof ApiError ? error.message : 'No se pudo iniciar sesión';
	}
}

export async function loadSession(): Promise<void> {
	try {
		const user = await api.get<SessionUser>('/auth/me');
		sessionUser.set(user);
	} catch {
		sessionUser.set(null);
	}
}

export async function logout(): Promise<void> {
	try {
		await api.post('/auth/logout', {});
	} finally {
		sessionUser.set(null);
	}
}
