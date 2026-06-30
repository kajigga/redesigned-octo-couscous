# pizza42 backend

Flask API for Pizza42 orders + menu. Auth0 RS256 (JWKS), SQLite storage.
See `PLAN.md` for design.

## Setup (uv)

```bash
# from backend/
uv sync                 # installs deps, creates .venv
cp .env.example .env    # then edit if needed
```

## Run (dev)

```bash
uv run python -m app    # dev server on http://localhost:8000
```

## Test

```bash
uv run pytest
```

## Endpoints

- `GET  /api/menu`   — public, returns pizzas/prices.
- `POST /api/orders` — auth (`Bearer` Auth0 access token, scope `pizza42-order`).
  Computes the total server-side from the menu. Body shape:
  `{ "items":[{"id":"pepperoni","quantity":2}], "address":{...} }`
  (a client-sent `total` is ignored).
- `GET  /api/orders` — auth; returns the caller's orders, newest first.

## Notes

- SQLite is a single `orders.db` file (created on first run). The `menu` table is
  reseeded idempotently on startup so price tweaks in `app/db.py` take effect.
- JWT verification fetches Auth0 JWKS (`<domain>/.well-known/jwks.json`) and resolves
  the signing key by `kid`. Audience `bongawonga-enterprises` and scope `pizza42-order`
  are enforced. Missing/invalid token → 401; valid token missing scope → 403.