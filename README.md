# Pizza42

A sample online pizza ordering application with two apps in one repo:

- **`frontend/`** — React + Vite SPA (Auth0 login, cart, checkout, profile)
- **`backend/`** — Flask API (menu, orders, backend by SQLite)

## Prerequisites

- **Node** `^20.19.0 || >=22.12.0`
- **Python** `>=3.11`
- **`uv`** (Python package manager) — install via `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`

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
- JWT verification: RS256 via Auth0 JWKS (key rotation handled). 
    - Missing/invalid token → 401;
    - valid token missing `pizza42-order` scope → 403.

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
├── Makefile                  # Deploy & run shortcuts
└── AGENTS.md                 # Development reference for AI assistants
```

## Notes

- **Storage**: SQLite (`instance/orders.db`), created on first run. `menu` table reseeded
  on startup. Not production-grade — no migrations beyond bootstrap.
- **Build system**: Backend uses `uv_build` (not hatchling, setuptools, etc.).
