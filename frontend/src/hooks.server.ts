import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit/hooks';

// Rutas públicas (no requieren sesión).
const PUBLIC_PREFIXES = ['/login', '/_app', '/brand', '/favicon', '/robots.txt'];

function isPublic(path: string): boolean {
	return PUBLIC_PREFIXES.some((prefix) => path === prefix || path.startsWith(`${prefix}/`));
}

function apiBase(): string {
	const runtime = globalThis as {
		process?: { env?: Record<string, string | undefined> };
	};
	return runtime.process?.env?.API_INTERNAL_URL ?? 'http://api:8000';
}

export const handle: Handle = async ({ event, resolve }) => {
	const path = event.url.pathname;
	if (isPublic(path)) {
		return resolve(event);
	}

	// Valida la sesión contra la API (mismo origen interno). Sin sesión -> /login.
	let authenticated = false;
	try {
		const cookie = event.request.headers.get('cookie') ?? '';
		const response = await fetch(`${apiBase()}/api/v1/auth/me`, { headers: { cookie } });
		authenticated = response.ok;
	} catch {
		authenticated = false;
	}

	if (!authenticated) {
		throw redirect(302, '/login');
	}
	return resolve(event);
};
