import { env } from '$env/dynamic/public';

import type { SessionUser } from '$lib/auth/session';

type RequestOptions = {
	method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
	token?: string;
	body?: unknown;
};

type ApiErrorBody = {
	detail?: string;
	[key: string]: unknown;
};

type PaginatedListResponse<T> = {
	results: T[];
};

const API_BASE_URL = env.PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

async function parseError(response: Response): Promise<string> {
	let data: ApiErrorBody | undefined;
	try {
		data = (await response.json()) as ApiErrorBody;
	} catch {
		return `Request failed with status ${response.status}.`;
	}

	if (typeof data?.detail === 'string') {
		return data.detail;
	}

	const firstEntry = Object.entries(data ?? {}).find(([, value]) => Boolean(value));
	if (!firstEntry) {
		return `Request failed with status ${response.status}.`;
	}

	const [field, value] = firstEntry;
	if (Array.isArray(value) && value[0]) {
		return `${field}: ${String(value[0])}`;
	}

	return `${field}: ${String(value)}`;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
	const { method = 'GET', token, body } = options;
	const headers: Record<string, string> = {
		'Content-Type': 'application/json'
	};
	if (token) {
		headers.Authorization = `Token ${token}`;
	}

	const response = await fetch(`${API_BASE_URL}${path}`, {
		method,
		headers,
		body: body ? JSON.stringify(body) : undefined
	});

	if (!response.ok) {
		throw new Error(await parseError(response));
	}

	if (response.status === 204) {
		return undefined as T;
	}

	return (await response.json()) as T;
}

function extractList<T>(payload: T[] | PaginatedListResponse<T>): T[] {
	if (Array.isArray(payload)) {
		return payload;
	}
	if (payload && Array.isArray(payload.results)) {
		return payload.results;
	}
	throw new Error('Unexpected list response format from server.');
}

export type AuthResponse = {
	token: string;
	user: SessionUser;
};

export function login(payload: { email: string; password: string }) {
	return request<AuthResponse>('/api/auth/login/', { method: 'POST', body: payload });
}

export function register(payload: {
	full_name: string;
	email: string;
	phone_number: string;
	password: string;
	password_confirm: string;
	national_id?: string;
}) {
	return request<AuthResponse>('/api/auth/register/', { method: 'POST', body: payload });
}

export function me(token: string) {
	return request<SessionUser>('/api/auth/me/', { token });
}

export function logout(token: string) {
	return request<void>('/api/auth/logout/', { method: 'POST', token });
}

export function updateProfile(
	token: string,
	payload: { full_name?: string; email?: string; phone_number?: string; national_id?: string }
) {
	return request<SessionUser>('/api/auth/me/', { method: 'PATCH', token, body: payload });
}

export type TransactionApi = {
	id: number;
	tx_type: string;
	direction: 'credit' | 'debit';
	amount: string;
	description: string;
	status: string;
	reference: string;
	external_reference: string;
	created_at: string;
};

export type DashboardSummaryResponse = {
	currency_code: string;
	savings_balance: string;
	active_loan_balance: string;
	next_repayment_date: string | null;
	total_shares: string;
	pending_deposit_count: number;
	pending_deposit_amount: string;
	recent_transactions: TransactionApi[];
};

export function fetchDashboardSummary(token: string) {
	return request<DashboardSummaryResponse>('/api/finance/dashboard/summary/', { token });
}

export function fetchTransactions(token: string, limit?: number) {
	const query = typeof limit === 'number' ? `?limit=${limit}` : '';
	return request<TransactionApi[] | PaginatedListResponse<TransactionApi>>(
		`/api/finance/transactions/${query}`,
		{ token }
	).then(extractList);
}

export type DepositResponse = {
	currency_code: string;
	transaction: TransactionApi;
	new_balance: string;
};

export function createDeposit(
	token: string,
	payload: { amount: number; payment_method: 'mtn' | 'airtel' | 'card' | 'bank'; phone_number?: string }
) {
	return request<DepositResponse>('/api/finance/deposits/', { method: 'POST', token, body: payload });
}

export type LoanApplicationApi = {
	id: number;
	member_name: string;
	member_email: string;
	amount: string;
	purpose: string;
	term_months: number;
	collateral_type: string;
	collateral_value: string | null;
	applicant_first_name: string;
	applicant_last_name: string;
	applicant_id_number: string;
	employer: string;
	monthly_salary: string | null;
	status: string;
	review_note: string;
	reviewer: number | null;
	reviewed_at: string | null;
	created_at: string;
	updated_at: string;
};

export function createLoanApplication(
	token: string,
	payload: {
		amount: number;
		purpose: string;
		term_months: number;
		collateral_type: string;
		collateral_value?: number;
		applicant_first_name: string;
		applicant_last_name: string;
		applicant_id_number: string;
		employer?: string;
		monthly_salary?: number;
	}
) {
	return request<LoanApplicationApi>('/api/finance/loans/applications/', {
		method: 'POST',
		token,
		body: payload
	});
}

export type LoanAccountApi = {
	id: number;
	application_id: number;
	principal: string;
	interest_rate: string;
	term_months: number;
	outstanding_balance: string;
	next_repayment_date: string | null;
	status: string;
	created_at: string;
};

export function fetchMyLoanAccounts(token: string) {
	return request<LoanAccountApi[] | PaginatedListResponse<LoanAccountApi>>(
		'/api/finance/loans/accounts/me/',
		{ token }
	).then(extractList);
}

export type StatementResponse = {
	currency_code: string;
	period: { start_date: string; end_date: string };
	opening_balance: string;
	closing_balance: string;
	total_credits: string;
	total_debits: string;
	transactions: TransactionApi[];
};

export function fetchCurrentStatement(token: string) {
	return request<StatementResponse>('/api/reports/statements/current/', { token });
}

export type AdminOverviewResponse = {
	currency_code: string;
	total_members: number;
	active_loans: number;
	total_deposits: string;
	loan_book: string;
	np_ratio: string;
	case_queue: number;
	total_transactions: number;
	total_notifications: number;
	failed_notifications: number;
};

export function fetchAdminOverview(token: string) {
	return request<AdminOverviewResponse>('/api/finance/admin/overview/', { token });
}

export type AdminActivityEventApi = {
	id: string;
	occurred_at: string;
	event_type: string;
	message: string;
	actor: string;
	severity: 'info' | 'action' | 'system';
};

export function fetchAdminActivity(token: string, limit = 12) {
	return request<AdminActivityEventApi[]>(`/api/finance/admin/activity/?limit=${limit}`, { token });
}

export function fetchAdminPendingLoans(token: string) {
	return request<LoanApplicationApi[] | PaginatedListResponse<LoanApplicationApi>>(
		'/api/finance/admin/loans/pending/',
		{ token }
	).then(extractList);
}

export function decideLoanApplication(
	token: string,
	applicationId: number,
	payload: { action: 'approve' | 'reject'; review_note?: string }
) {
	return request<LoanApplicationApi>(`/api/finance/admin/loans/${applicationId}/decision/`, {
		method: 'POST',
		token,
		body: payload
	});
}

export type TransferResponse = {
	currency_code: string;
	transaction: TransactionApi;
	new_balance: string;
};

export function createTransfer(
	token: string,
	payload: {
		transfer_type: 'internal' | 'external';
		destination: string;
		amount: number;
		note?: string;
	}
) {
	return request<TransferResponse>('/api/finance/transfers/', { method: 'POST', token, body: payload });
}

export type WithdrawalResponse = {
	currency_code: string;
	transaction: TransactionApi;
	new_balance: string;
};

export function createWithdrawal(
	token: string,
	payload: {
		destination_type: 'bank' | 'mobile';
		amount: number;
		bank_name?: string;
		account_number?: string;
		routing_number?: string;
		mobile_network?: 'mtn' | 'airtel';
		phone_number?: string;
	}
) {
	return request<WithdrawalResponse>('/api/finance/withdrawals/', { method: 'POST', token, body: payload });
}
