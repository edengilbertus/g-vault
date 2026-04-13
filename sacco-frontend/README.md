# G Vault Frontend

SvelteKit frontend for G Vault SACCO banking.

## Local setup

```sh
cd sacco-frontend
npm install
cp .env.example .env
npm run dev
```

Default app URL: `http://localhost:5173`

## Backend connection

Set these in `.env`:

```sh
PUBLIC_API_BASE_URL=http://127.0.0.1:8000
PRIVATE_API_BASE_URL=http://127.0.0.1:8000
```

The frontend expects the Django backend to be running and exposes:
- auth (`/api/auth/*`)
- finance (`/api/finance/*`)
- reports (`/api/reports/*`)

## Optional SMS alerts

To enable transfer SMS notifications via Africa's Talking, set:

```sh
AT_USERNAME=your_username
AT_API_KEY=your_api_key
```
