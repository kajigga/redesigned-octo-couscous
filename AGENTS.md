# AGENTS.md

Pizza42 — `frontend/` (React/Vite, SPA) + `backend/` (Flask API). Backend per `backend/PLAN.md`.

## Commands

| Area | Command |
|------|---------|
| Frontend dev | `npm run dev` (from `frontend/`) |
| Auth0 config | `npm run auth0-config -- --domain <d> --clientId <id> [--port <p>]` |
| Frontend lint | `npm run lint` |
| Frontend test | `npm test` / `npm run test:watch` / `npm run test:coverage` |
| Single test | `npx jest __tests__/auth0-config.test.cjs` |
| Backend deps | `uv sync` |
| Backend dev | `uv run python -m app` |
| Backend test | `uv run pytest` |
| Add backend dep | `uv add <pkg>` |

## Auth0

- **Domain**: `bongawonga.us.auth0.com` · **Audience**: `bongawonga-enterprises` · **Scope**: `pizza42-order`
- **Issuer**: `https://bongawonga.us.auth0.com/` · **JWKS**: `…/.well-known/jwks.json`
- Frontend `.env.local` (`VITE_`-prefixed; `VITE_AUTH0_AUDIENCE` hand-maintained) · Backend `.env`

## Gotchas

- **Port**: `npm run dev` checks `PORT` from `.env.local`. If taken, Auth0 callback URLs break — free the port, don't change `PORT`.
- **Tests**: jest only covers `tools/**/*.cjs` (CommonJS). `src/` is ESM/JSX — no tests; adding needs babel/swc config.
- **Prettier**: 2-space, no tabs. No format script — `npx prettier -w .`
- **Node**: `^20.19.0 \|\| >=22.12.0` (`.npmrc engine-strict=true`)
- **Backend build**: uses `uv_build`
- **Add backend deps**: always use `uv add <pkg>` — never edit `pyproject.toml` manually
- **Semantic versioning**: Frontend and backend have independent semver versions. Backend: `uv version --bump <part>` (or `make bump-backend PART=<part>`). Frontend: `npm version <part> --no-git-tag-version` (or `make bump-frontend PART=<part>`).
- **`quickstart/`**: Auth0 data, not app source

## Repo Hygiene

- **Don't commit plans, handoff docs, or scratch markdown** unless explicitly told to do so
- **Delete outdated plans** (like `backend/PLAN.md`) once the work is complete
- **Keep the repo clean** — only commit code, tests, and essential documentation
- **Always use a checklist** for multi-step tasks — create todos and work through them systematically

## Git Workflow

- **Always pull from main** before starting work: `git checkout main && git pull`
- **Work in feature branches** — never commit directly to main
  - Features: `git checkout -b feature/name`
  - Bug fixes: `git checkout -b fix/name`
  - Chores: `git checkout -b chore/name`
- **Create PRs** for review, then merge via GitHub
- Version bumps happen automatically on merge (see Contributing section in README)

## Before done

`npm run lint && npm test` (frontend/), `uv run pytest` (backend/). Confirm `npm run dev` starts.
