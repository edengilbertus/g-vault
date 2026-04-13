import { env } from '$env/dynamic/private';
import { redirect, type Handle } from '@sveltejs/kit';

type SessionUser = {
	id: number;
	email: string;
	full_name: string;
	phone_number: string;
	national_id: string | null;
	is_staff: boolean;
	date_joined: string;
};

const API_BASE_URL = env.PRIVATE_API_BASE_URL || env.PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';
const AUTH_COOKIE = 'gv_token';

const memberProtectedPrefix = '/dashboard';
const adminProtectedPrefix = '/admin';

async function fetchAuthenticatedUser(token: string): Promise<SessionUser | null> {
	try {
		const response = await fetch(`${API_BASE_URL}/api/auth/me/`, {
			headers: {
				Authorization: `Token ${token}`,
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			return null;
		}

		return (await response.json()) as SessionUser;
	} catch {
		return null;
	}
}

export const handle: Handle = async ({ event, resolve }) => {
	const token = event.cookies.get(AUTH_COOKIE);
	const path = event.url.pathname;

	if (token) {
		const user = await fetchAuthenticatedUser(token);
		if (user) {
			event.locals.user = user;
			event.locals.token = token;
		}
	}

	if (!event.locals.user && (path.startsWith(memberProtectedPrefix) || path.startsWith(adminProtectedPrefix))) {
		throw redirect(302, '/');
	}

	if (event.locals.user && path === '/') {
		throw redirect(302, event.locals.user.is_staff ? '/admin' : '/dashboard');
	}

	if (event.locals.user && path.startsWith(memberProtectedPrefix) && event.locals.user.is_staff) {
		throw redirect(302, '/admin');
	}

	if (event.locals.user && path.startsWith(adminProtectedPrefix) && !event.locals.user.is_staff) {
		throw redirect(302, '/dashboard');
	}

	return resolve(event);
};
