import { startAuthentication, startRegistration } from '@simplewebauthn/browser';
import { api } from './api/client';
import type { SessionUser } from './stores/session';

type RegOptions = Parameters<typeof startRegistration>[0]['optionsJSON'];
type AuthOptions = Parameters<typeof startAuthentication>[0]['optionsJSON'];

export function webAuthnSupported(): boolean {
	return typeof window !== 'undefined' && typeof window.PublicKeyCredential !== 'undefined';
}

export async function registerPasskey(name?: string): Promise<{ id: string; name: string }> {
	const options = await api.post<RegOptions>('/auth/webauthn/register/begin');
	const credential = await startRegistration({ optionsJSON: options });
	return api.post<{ id: string; name: string }>('/auth/webauthn/register/complete', {
		credential,
		name
	});
}

export async function loginWithPasskey(email?: string): Promise<SessionUser> {
	const options = await api.post<AuthOptions>('/auth/webauthn/login/begin', email ? { email } : {});
	const credential = await startAuthentication({ optionsJSON: options });
	return api.post<SessionUser>('/auth/webauthn/login/complete', { credential });
}

/** Intenta login con passkey vía autocompletado (sugerencia del navegador). */
export async function conditionalPasskeyLogin(): Promise<SessionUser | null> {
	if (!webAuthnSupported()) return null;
	const available = await PublicKeyCredential.isConditionalMediationAvailable?.();
	if (!available) return null;
	const options = await api.post<AuthOptions>('/auth/webauthn/login/begin', {});
	const credential = await startAuthentication({ optionsJSON: options, useBrowserAutofill: true });
	return api.post<SessionUser>('/auth/webauthn/login/complete', { credential });
}
