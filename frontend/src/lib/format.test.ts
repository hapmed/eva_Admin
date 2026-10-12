import { describe, expect, it } from 'vitest';
import { formatDate, joinOrDash } from './format';

describe('formatDate', () => {
	it('recorta a la parte de fecha', () => {
		expect(formatDate('2026-10-11T13:45:00Z')).toBe('2026-10-11');
	});

	it('usa un guion cuando no hay valor', () => {
		expect(formatDate(null)).toBe('—');
		expect(formatDate(undefined)).toBe('—');
	});
});

describe('joinOrDash', () => {
	it('une los elementos con coma', () => {
		expect(joinOrDash(['a', 'b'])).toBe('a, b');
	});

	it('usa un guion cuando la lista está vacía', () => {
		expect(joinOrDash([])).toBe('—');
	});
});
