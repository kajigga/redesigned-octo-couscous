# Next Session: Phase 2 — Deploy to Docker Host with MySQL

## What's Done

### Phase 1 ✅ — Local Dev with MySQL
- Backend connects to DigitalOcean MySQL successfully
- `/api/menu` returns 3 seeded pizzas from MySQL
- `/api/version` works with `RENDER_GIT_COMMIT` fallback
- `uv run pytest` passes (11/11 tests)

### Phase 6 ✅ — Semantic Versioning
- Backend: `pyproject.toml` version + git SHA in `/api/version`
- Frontend: `package.json` version shown in Footer
- Makefile targets: `make bump-backend PART=patch`, `make bump-frontend PART=patch`
- GitHub Action: Auto-bumps versions on PR merge (reads labels `bump:major/minor/patch`)

## Next Steps: Phase 2

### 2.1 — Verify Docker deployment with MySQL
The `DATABASE_URL` is already in `backend/.env`. The Makefile's `deploy-backend` target:
1. rsyncs backend code to ARM host
2. SCPs `backend/.env` to `backend.env` on the host
3. Appends `GIT_SHA` to `backend.env`
4. Rebuilds and restarts the Docker container

**Action:** Run `make deploy-backend` and verify the live backend works against MySQL.

### 2.2 — Verify live backend
- Test `https://orders.pizza42.bongawonga.com/api/menu` returns items
- Test `https://orders.pizza42.bongawonga.com/api/version` returns SHA

### 2.3 — Potential Issues
- Docker container needs `pymysql` installed (should be in Dockerfile via `uv sync`)
- MySQL SSL connection needs to work from the ARM host (DigitalOcean cluster requires SSL)
- The `SQLALCHEMY_ENGINE_OPTIONS` with SSL is set in `__init__.py` conditionally for MySQL

## Files Changed in This Session
```
.github/workflows/bump-version.yml  (new)
AGENTS.md                           (updated)
Makefile                            (updated)
PLAN-supabase-render.md             (updated)
backend/.env                        (updated - MySQL connection string)
backend/.env.example                (updated)
backend/app/__init__.py             (updated - conditional SSL for MySQL)
backend/app/models.py               (updated - VARCHAR lengths)
backend/app/routes/public_endpoints.py  (updated - RENDER_GIT_COMMIT fallback)
backend/pyproject.toml              (updated - pymysql dependency)
backend/uv.lock                     (updated)
```

## Key Commands for Next Session
```bash
# Deploy backend to Docker host
make deploy-backend

# Verify live backend
curl https://orders.pizza42.bongawonga.com/api/menu
curl https://orders.pizza42.bongawonga.com/api/version

# Bump versions (if needed)
make bump-backend PART=patch
make bump-frontend PART=patch
```

## Branch
`supabase-render-migration` — commit `c016cd4`
