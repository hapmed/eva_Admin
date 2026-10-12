const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export class ApiError extends Error {
	readonly status: number;

	constructor(status: number, message: string) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
	}
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
	const response = await fetch(`${BASE_URL}${path}`, {
		credentials: 'include',
		headers: { Accept: 'application/json', ...(init?.headers ?? {}) },
		...init
	});
	if (!response.ok) {
		throw new ApiError(response.status, `Solicitud fallida (${response.status})`);
	}
	return (await response.json()) as T;
}
