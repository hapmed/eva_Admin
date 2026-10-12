export function formatDate(value: string | null | undefined): string {
	return value ? value.slice(0, 10) : '—';
}

export function joinOrDash(values: string[]): string {
	return values.length ? values.join(', ') : '—';
}
