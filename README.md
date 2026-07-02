# Pizza42
![pic alt](https://pizza42.bongawonga.com/images/pizza42_logo.png "opt title")
A sample online pizza ordering application with two apps in one repo:

- **`frontend/`** — React + Vite SPA (Auth0 login, cart, checkout, profile)
- **`backend/`** — Flask API (menu, orders)

## Prerequisites

- **Node** 
- **Python**
- **`uv`** (Python package manager)

## Auth0

This project uses a shared Auth0 tenant for authentication.

| Setting     | Value                               |
|-------------|-------------------------------------|
| Domain      | `bongawonga.us.auth0.com`           |
| Audience    | `bongawonga-enterprises`            |
| Scope(required for order completion)       | `pizza42-order`                     |
| Issuer      | `https://bongawonga.us.auth0.com/`  |
| JWKS URI    | `https://bongawonga.us.auth0.com/.well-known/jwks.json` |

- **Frontend** — Auth0 config is stored in `frontend/.env.local` (vars prefixed with `VITE_`).
  Use `npm run auth0-config -- --domain bongawonga.us.auth0.com --clientId <id> --port 5173`
  to populate it. `VITE_AUTH0_AUDIENCE` is hand-maintained.
- **Backend** — reads from `backend/.env` (see `backend/.env.example`).
- **Signup & social login** (Google) are handled by Auth0's Universal Login page itself — the application delegates authentication entirely to Auth0 and does not manage credentials or identity providers directly.
- email validation is handles by an Auth0 form at checkout time if it hasn't already been done.
- JWT verification without introspection:
    - Missing/invalid token → 401;
    - valid token missing `pizza42-order` scope → 403.

## Project Structure

```
pizza42/
├── frontend/                 # React + Vite SPA
│   ├── src/                  # App source (components, context, API client)
│   ├── tools/                # CommonJS scripts (auth0-config, check-port)
│   ├── quickstart/           # Auth0 quickstart data (not app source)
│   ├── Dockerfile            # Multi-stage build: node build → nginx serve
│   ├── nginx.conf            # SPA nginx config (try_files /index.html)
│   └── .env.local            # Local Auth0 config (gitignored)
├── backend/                  # Flask API
│   ├── app/                  # App package (routes, models, db)
│   ├── tests/                # pytest tests
│   ├── Dockerfile            # Python 3.11-slim, gunicorn
│   ├── pyproject.toml        # uv_build, deps
│   └── .env.example          # Template for backend .env
├── auth0_actions/            # Auth0 Login Action scripts (email verification, address collection, order claims)
├── Makefile                  # Deploy & run shortcuts
└── AGENTS.md                 # Development reference for AI assistants
```

## API Endpoints

| Method | Path           | Auth Required | Description                          |
|--------|----------------|---------------|--------------------------------------|
| GET    | `/api/menu`    | No            | Returns pizzas and prices            |
| POST   | `/api/orders`  | Yes           | Place an order (scope `pizza42-order`) |
| GET    | `/api/orders`  | Yes           | Returns the caller's orders          |

**POST /api/orders** body shape:
```json
{
  "items": [{"id": "pepperoni", "quantity": 2}],
  "address": { ... }
}
```

The `total` sent by the client is ignored — it is computed server-side from the menu table.

## Auth0 Actions

Three custom Login Actions are deployed in the Auth0 tenant, triggered on every login to the Pizza42 app. They branch on whether the `pizza42-order` scope is requested to modify the flows.

- **[`auth0_actions/p42-check-email-intent.js`](auth0_actions/p42-check-email-intent.js)** — Email verification

- **[`auth0_actions/p42-check-address.js`](auth0_actions/p42-check-address.js)** — Progressive profiling via an Auth0 Form. When a user logs in with order intent, this action renders an address collection form. The address is saved to `user_metadata` and injected as `pizza42/address_*` custom claims into the ID token. On subsequent logins without order intent, the stored address claims are added to the ID token without re-prompting.

- **[`auth0_actions/p42-orders.js`](auth0_actions/p42-orders.js)** — Reads `app_metadata.pizza42/orders` and injects it as the `pizza42/orders` custom claim into the ID token on every login, so order history is available client-side without an extra API call.

## Deployment

Production runs on an ARM host (`arm`) via Docker Compose. From the repo root:

```bash
make deploy-backend      # rsync backend/ → host, build & restart Docker container
make deploy-frontend     # build react/Vite app → rsync dist/ + nginx.conf → host, restart container
make deploy              # both of the above
```

- **Frontend** is served by nginx (static files from `dist/`), Docker image based on `nginx:alpine`.
- **Backend** runs with gunicorn (4 workers), Docker image based on `python:3.11-slim`.
- Secrets (`backend/.env`) are scp'd separately, not rsynced.
- The `Makefile` excludes `.git`, `node_modules`, `.venv`, `dist` and other generated/private files.


## Local Development

### Frontend

```bash
cd frontend
npm install
make run-frontend              # dev server on http://localhost:5173
```

### Backend

```bash
cd backend
cp .env.example .env       # edit if needed
make run-backend       # dev server on http://localhost:8000
```

### Makefile shortcuts

From the repo root:

```bash
make run-frontend     # cd frontend && npm run dev
make run-backend      # cd backend && uv run python -m app
```

## Notes

- **Storage**: SQLite (`instance/orders.db`), created on first run. `menu` table refilled on startup
- **Build system**: Backend uses `uv_build` (not hatchling, setuptools, etc.).
