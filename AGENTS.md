# AGENTS.md

Pizza42 online ordering — a two-app project in one repo.
- `frontend/` — React + Vite SPA (Auth0 login, cart, checkout, profile)
- `backend/`  — Flask API (orders + menu). Build status: see `backend/PLAN.md`

## Commands

### Frontend (run from `frontend/`)
- Dev: `npm run dev` (runs `node tools/check-port.cjs && vite`). Port check fails if
  `PORT` (from `.env.local`) is taken — Auth0 callback/logout/origin URLs must match. Free
  the port; don't change `PORT` without updating Auth0 settings.
- Auth0 config: `npm run auth0-config -- --domain <d> --clientId <id> [--port <p>]`.
  Writes `.env.local`; manages only `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, `PORT`.
  `VITE_AUTH0_AUDIENCE` is hand-maintained.
- Lint: `npm run lint`. Test: `npm test` / `npm run test:watch` / `npm run test:coverage`.
- Single test: `npx jest __tests__/auth0-config.test.cjs`.

### Backend (run from `backend/`)
- Install deps: `uv sync` (creates `.venv`).
- Dev server: `uv run python -m app` (port from `.env`, default 8000).
- Tests: `uv run pytest`.
- Add a dep: `uv add <pkg>`.
- Not yet built — implement per `backend/PLAN.md`.

## Shared Auth0
- Domain: `bongawonga.us.auth0.com` · Audience: `bongawonga-enterprises` · Scope: `pizza42-order`
- Issuer: `https://bongawonga.us.auth0.com/`; JWKS: `…/.well-known/jwks.json`
- Frontend reads from `frontend/.env.local` (vars consumed in `src/` must be `VITE_`-prefixed).
- Backend reads from `backend/.env` (see `backend/.env.example`).

## Architecture overview
- Frontend entrypoints: `frontend/src/main.jsx` (Auth0Provider) → `frontend/src/App.jsx`
  (BrowserRouter + CartProvider + Routes). `/` and `/cart` are public; `/checkout` and
  `/profile` are wrapped in `ProtectedRoute`.
- After login, `App.jsx` restores the route saved to `sessionStorage["auth0_return_to"]`
  by `onRedirectCallback` in `main.jsx`.
- Cart state: `frontend/src/context/CartContext.jsx` (`useReducer`, persisted to
  localStorage), exposed via `useCart()`.
- API: `frontend/src/api/client.js` posts to a base URL with
  `Authorization: Bearer <token>`. Currently `https://orders.bongawonga.com` (a
  placeholder — no real backend exists yet); once the backend is wired up it should point
  to `http://localhost:8000`. `orders.js` does `POST /api/orders`; a `GET /api/orders` and
  `GET /api/menu` call will be added then.
- `Profile.jsx` currently reads `user["pizza42/orders"]` or falls back to mocks — to be
  replaced with a `GET /api/orders` call (follow-up).
- Backend serves the menu from a SQLite `menu` table; `POST /api/orders` recomputes the
  total server-side from that table (client-sent `total` is ignored).

## Frontend notes (high-signal)
- Package is `"type": "module"` (ESM). `tools/*.cjs` are CommonJS and run under Node directly.
- Node engine enforced via `.npmrc engine-strict=true`: `^20.19.0 || >=22.12.0`.
- ESLint: `no-unused-vars` ignores names matching `^[A-Z_]` (intentional unused JSX vars).
  Don't "fix" these by removing them unless truly dead. ESM flat config in `eslint.config.js`.
- Prettier: 2-space, no tabs (`.prettierrc`). No `format` script — run `npx prettier -w .`.
- `check-port.cjs` reads `quickstart/quickstart-login.yaml` for the env file name, then
  reads `PORT` from that env file. Default port differs across files (vite 5173,
  check-port 3000) — rely on `.env.local` to keep them consistent.
- Vite loads `.env.local` itself (`vite.config.js` also calls `dotenv.config`).
- `quickstart/` is Auth0 quickstart content (markdown/scripts/yaml) that the config tools
  read from; treat it as data, not app source.

## Frontend testing gotcha
`jest.config.cjs` matches `**/__tests__/**/*.test.cjs` and collects coverage only from
`tools/**/*.cjs`. Tests exist **only for the `tools/` scripts** — the React app under
`src/` has no tests. Adding `src/` tests requires config changes (jest is CommonJS/`.cjs`,
`src/` is ESM/`.jsx` — needs e.g. `@babel/preset-react`/`@swc/jest`).

## Backend notes
- See `backend/PLAN.md` for the full spec until the backend is built.
- JWT validation: RS256 via Auth0 JWKS (key rotation handled), audience + issuer + scope
  `pizza42-order` enforced. Unauthorized → 401; valid token but missing scope → 403.
- Storage: SQLite (`orders.db`), `menu`/`orders`/`order_items` tables, menu seeded on
  startup. Not production-grade; no migrations beyond bootstrap.
- Build backend: **`uv_build`** (not hatchling, setuptools, etc.). Every Python project
  in this repo uses `uv_build` with `[tool.uv.build-backend]` configured as needed.

## Before considering work done
- Frontend: `npm run lint` then `npm test` (run from `frontend/`).
- Backend: `uv run pytest` (run from `backend/`).
- No typecheck script (JSX/Python without mypy configured).
- For dev-server changes: confirm `npm run dev` starts without a port error.