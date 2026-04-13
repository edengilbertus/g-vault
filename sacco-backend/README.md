# SACCO Backend (Django + DRF)

Backend API for the SACCO frontend, covering:
- member auth and profile identity
- savings/deposit/transfer/withdrawal transaction flows
- loan application and admin review/disbursement
- mobile money webhook intake
- account statement reporting

## 1. Setup

```bash
cd sacco-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 2. Auth for frontend

Use token auth:
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `POST /api/auth/logout/`

Pass auth header:

```text
Authorization: Token <token>
```

## 3. Core endpoints

- `GET /api/health/`
- `GET /api/finance/dashboard/summary/`
- `GET /api/finance/transactions/`
- `POST /api/finance/deposits/`
- `POST /api/finance/transfers/`
- `POST /api/finance/withdrawals/`
- `POST /api/finance/loans/applications/`
- `GET /api/finance/loans/applications/me/`
- `GET /api/finance/loans/accounts/me/`
- `GET /api/finance/admin/overview/` (admin only)
- `GET /api/finance/admin/activity/` (admin only)
- `GET /api/finance/admin/loans/pending/` (admin only)
- `POST /api/finance/admin/loans/<id>/decision/` (admin only)
- `POST /api/comms/webhooks/mobile-money/`
- `GET /api/reports/statements/current/`

## 4. SMS notifications (Africa's Talking)

Set in `.env`:

```text
AT_USERNAME=your_username
AT_API_KEY=your_api_key
```

With these configured, backend SMS notifications are sent for:
- deposits
- transfers
- withdrawals
- loan approval/rejection decisions

Mobile money deposits (`mtn` / `airtel`) are created as `pending` and only move to `completed`
after a success callback to `POST /api/comms/webhooks/mobile-money/` using the deposit reference
as `transactionId`.
