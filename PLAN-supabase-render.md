# Plan: Supabase + Render Migration

Branch: `supabase-render-migration`

## Overview

Migrate Pizza42 from local SQLite + Docker deployment to Supabase PostgreSQL + Render hosting.

## Phase 1 — Local Dev with Supabase

**1.1** Create a free Supabase project at supabase.com, copy the connection string (`Settings → Database → Connection string`).

**1.2** Add PostgreSQL driver to `backend/pyproject.toml`:
```
dependencies = [..., "psycopg2-binary>=2.9"]
```

**1.3** Run `uv sync && uv lock` to update lockfile.

**1.4** Add `DATABASE_URL` to `backend/.env`:
```
DATABASE_URL=postgresql://postgres:<pw>@db.<ref>.supabase.co:5432/postgres?sslmode=require
```

**1.5** Start the backend locally — `uv run python -m app`. Verify:
- `/api/menu` returns seeded items (from the new PostgreSQL DB)
- `/api/version` works
- `uv run pytest` passes (tests use temp SQLite, unaffected)

## Phase 2 — Deploy to Current Docker Host

**2.1** Add `DATABASE_URL` to the backend `.env` that gets SCP'd to the ARM host during `make deploy-backend`.

**2.2** Run `make deploy-backend` — Docker rebuilds with `psycopg2-binary` and picks up the new env var.

**2.3** Verify the live backend at `orders.pizza42.bongawonga.com` still works against Supabase.

## Phase 3 — Frontend → Render Static Site

**3.1** In Render dashboard: **New + → Static Site**, connect the GitHub repo.

| Setting | Value |
|---------|-------|
| Root directory | `frontend/` |
| Build command | `npm ci && VITE_GIT_SHA=${RENDER_GIT_COMMIT:-} npm run build` |
| Publish directory | `dist` |
| SPA routing | Enable **"Redirect not found" → `/index.html`** |

**3.2** Set env vars in Render dashboard:
```
VITE_AUTH0_DOMAIN=bongawonga.us.auth0.com
VITE_AUTH0_CLIENT_ID=hqvoam0pzpABmubbw2Hgq026cjctsfqP
VITE_AUTH0_AUDIENCE=bongawonga-enterprises
VITE_API_BASE_URL=https://api.pizza42.bongawonga.com
```

**3.3** Add custom domain `pizza42.bongawonga.com` → CNAME to `pizza42.bongawonga.com.onrender.com`.

## Phase 4 — Backend → Render Web Service (Native Python)

**4.1** In Render dashboard: **New + → Web Service**, connect the same repo.

| Setting | Value |
|---------|-------|
| Root directory | `backend/` |
| Runtime | Python 3 (auto-detected) |
| Build command | `pip install uv && uv sync --frozen --no-dev` |
| Start command | `uv run gunicorn -w 4 -b 0.0.0.0:$PORT "app:create_app()"` |
| Plan | Free |

**4.2** Set env vars in Render dashboard:
```
AUTH0_DOMAIN=bongawonga.us.auth0.com
AUTH0_AUDIENCE=bongawonga-enterprises
AUTH0_SCOPE=pizza42-order
AUTH0_MGMT_CLIENT_ID=<from .env>
AUTH0_MGMT_CLIENT_SECRET=<from .env>
FLASK_SECRET_KEY=<from .env>
DATABASE_URL=<Supabase connection string>
```

**4.3** Update `/api/version` endpoint to also read `RENDER_GIT_COMMIT` (Render's built-in env var):

In `backend/app/routes/public_endpoints.py`:
```python
version = (os.environ.get("GIT_SHA")
           or os.environ.get("RENDER_GIT_COMMIT", "unknown"))
```

**4.4** Add custom domain `api.pizza42.bongawonga.com` → CNAME to `api.pizza42.bongawonga.com.onrender.com`.

## Phase 5 — DNS & Verification

**5.1** Update DNS with name.com:
- Add `pizza42.bongawonga.com` CNAME → Render frontend
- Add `api.pizza42.bongawonga.com` CNAME → Render backend
- Remove or keep `orders.pizza42.bongawonga.com` (up to you)

**5.2** End-to-end test:
- Browse `pizza42.bongawonga.com` → menu loads → Auth0 login → place order
- `api.pizza42.bongawonga.com/version` returns SHA
- `api.pizza42.bongawonga.com/menu` returns items

**5.3** When confirmed working, clean up the Docker containers on the ARM host.

## Files Modified (Summary)

| File | Change |
|------|--------|
| `backend/pyproject.toml` | Add `psycopg2-binary` dependency |
| `backend/uv.lock` | Auto-updated by `uv lock` |
| `backend/.env` | Add `DATABASE_URL` |
| `backend/app/routes/public_endpoints.py` | Fall back to `RENDER_GIT_COMMIT` |

Everything else (Dockerfiles, Makefile, nginx.conf) stays — the Docker deployment remains functional as a fallback.
