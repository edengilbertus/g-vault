import { browser } from '$app/environment';

export type SessionUser = {
	id: number;
	email: string;
	full_name: string;
	phone_number: string;
	national_id: string | null;
	is_staff: boolean;
	date_joined: string;
};

const TOKEN_KEY = 'gv_token';
const USER_KEY = 'gv_user';
const COOKIE_NAME = 'gv_token';
const THIRTY_DAYS = 60 * 60 * 24 * 30;

function getCookie(name: string): string | null {
	if (!browser) return null;
	const prefix = `${name}=`;
	const cookies = document.cookie.split(';');
	for (const rawCookie of cookies) {
		const cookie = rawCookie.trim();
		if (cookie.startsWith(prefix)) {
			return decodeURIComponent(cookie.slice(prefix.length));
		}
	}
	return null;
}

export function getStoredToken(): string | null {
	if (!browser) return null;
	return localStorage.getItem(TOKEN_KEY) ?? getCookie(COOKIE_NAME);
}

export function getStoredUser(): SessionUser | null {
	if (!browser) return null;
	const raw = localStorage.getItem(USER_KEY);
	if (!raw) return null;
	try {
		return JSON.parse(raw) as SessionUser;
	} catch {
		return null;
	}
}

export function persistSession(token: string, user: SessionUser): void {
	if (!browser) return;
	localStorage.setItem(TOKEN_KEY, token);
	localStorage.setItem(USER_KEY, JSON.stringify(user));
	document.cookie = `${COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; Max-Age=${THIRTY_DAYS}; SameSite=Lax`;
}

export function clearSession(): void {
	if (!browser) return;
	localStorage.removeItem(TOKEN_KEY);
	localStorage.removeItem(USER_KEY);
	document.cookie = `${COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`;
}
