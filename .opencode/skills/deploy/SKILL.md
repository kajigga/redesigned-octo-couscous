---
name: deploy
description: Use ONLY when deploying the pizza42 frontend or backend to production. Run `make deploy-frontend` or `make deploy-backend` from the repo root — never run individual rsync/ssh/compose commands. The Makefile handles the full workflow (build, rsync, container restart).
---

# Deploy — pizza42

Always deploy via the Makefile targets from the repo root (`/Users/kevin/dev/pizza42`).

## Frontend `make deploy-frontend`

1. Runs `build-frontend` (which does `npm ci && VITE_API_BASE_URL=https://orders.pizza42.bongawonga.com npm run build` — overrides the dev `.env.local` value)
2. Rsyncs `frontend/dist/`, `frontend/nginx.conf`, and `frontend/.env.production` to the `arm` host
3. Runs `docker compose up -d pizza42-frontend` on arm (restarts the nginx container with new files; no image build)

**Do NOT** run individual rsync/ssh/compose commands yourself — always use `make deploy-frontend`.

## Backend `make deploy-backend`

1. Rsyncs `backend/` source to arm
2. Copies `backend/.env` as secrets file
3. Runs `docker compose build pizza42-backend && docker compose up -d pizza42-backend` on arm (backend changes require a full image rebuild)

## Fallback `make deploy-frontend-image`

Uses the Dockerfile to build a baked nginx image instead of the volume-mount approach. Only needed if the volume-mount approach has issues.

## Infrastructure

| Host | Alias | Role |
|------|-------|------|
| `10.10.0.68` | `arm` | Docker host; runs compose for pizza42 services |
| `10.10.0.64` | `loadbalancer` | HAProxy + acme.sh TLS termination |

- Frontend → `arm:8081` → HAProxy `https://pizza42.bongawonga.com`
- Backend → `arm:8002` → HAProxy `https://orders.pizza42.bongawonga.com`

## Verify after deploy

```sh
curl -s -o /dev/null -w '%{http_code}' https://pizza42.bongawonga.com/             # frontend → 200
curl -s https://orders.pizza42.bongawonga.com/api/menu | head -c 100               # backend → JSON
```
