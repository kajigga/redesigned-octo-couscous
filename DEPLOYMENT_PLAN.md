# Deployment Plan — Pizza42 dockerized deployment + reusable add-hostname tooling

Status: **executing.** Steps 1-3 done; step 4 (restart opencode) pending user.
Decisions locked. Build order below.

### Progress log
- [x] **Step 1** — `op` confirmed working; vault `Private`; item `Name.com` has fields `username` (`kajigga`) and `api_token`.
- [x] **Step 2** — `namecom` MCP server added to `~/.config/opencode/opencode.jsonc` (creds via `{env:NAMECOM_*}`, resolved by `op read` before launch).
- [x] **Step 3** — `add-hostname` skill created at `~/.config/opencode/skills/add-hostname/` (`SKILL.md` + `add_hostname.py`). Script uses **PEP 723 inline metadata** (no `pyproject.toml`) and shells out to `ssh loadbalancer` via `subprocess` (paramiko can't read the Keychain-unlocked encrypted key). Verified with `--dry-run` against the live loadbalancer.
- [ ] **Step 4** — user restarts opencode (loads MCP + skill).
- **Note:** DNS for `pizza42.bongawonga.com` and `orders.pizza42.bongawonga.com` is already configured (both resolve to the loadbalancer public IP `104.243.54.235`). Step 7 needs HAProxy + cert only — no DNS via MCP.

---

## Part 0 — Prerequisites (user handles)

1. **`op` works** (runs fine in user's terminal); no perms fix needed.
2. **Auth0 dashboard** (can be done anytime, required before login works on new domain):
   for app `hqvoam0pzpABmubbw2Hgq026cjctsfqP` add `https://pizza42.bongawonga.com` to:
   - Allowed Callback URLs
   - Allowed Logout URLs
   - Allowed Web Origins
   (`redirect_uri` in `frontend/src/main.jsx` uses `window.location.origin`.)

## Part 1 — Reusable `add-hostname` tooling (global opencode skill + MCP server)

Built **first** so pizza42's DNS/HAProxy/cert steps dogfood it.

### 1a. name.com MCP server (opencode global config)

Add to `~/.config/opencode/opencode.json` `mcp` section (per customize-opencode skill; `{env:VAR}` interpolation):

```json
{
  "mcp": {
    "namecom": {
      "type": "local",
      "command": ["npx", "-y", "namecom-mcp@latest"],
      "env": {
        "NAME_USERNAME": "{env:NAMECOM_USERNAME}",
        "NAME_TOKEN": "{env:NAMECOM_TOKEN}",
        "NAME_API_URL": "https://mcp.name.com"
      },
      "enabled": true
    }
  }
}
```

Credentials resolved from shell environment, set by `op read` before launching opencode (per user preference):
```bash
export NAMECOM_USERNAME=$(op read 'op://<vault>/Name.com/username')
export NAMECOM_TOKEN=$(op read 'op://<vault>/Name.com/api_token')
```
- 1Password item: `Name.com`, fields `username` and `api_token`.
- Vault name: **Private** — references `op://Private/Name.com/username` and `op://Private/Name.com/api_token`.
- Sandbox switch for dry-runs: unset `NAME_API_URL` (defaults to `mcp.dev.name.com`) and use `-test` username.

### 1b. `add_hostname.py` Python helper (PEP 723 inline metadata, global skill dir)

Lives at `~/.config/opencode/skills/add-hostname/`. No `pyproject.toml` —
deps declared in the script header (PEP 723), so `uv run` auto-installs them:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
```
Run: `uv run add_hostname.py …`

**The script** (`add_hostname.py`, argparse CLI, idempotent, `--dry-run`):
- SSH via the **`loadbalancer` SSH alias** (`ssh -o BatchMode=yes loadbalancer …`). macOS OpenSSH pulls the encrypted `~/.ssh/id_ecdsa` passphrase from the Keychain (`UseKeychain`); paramiko can't, so the script uses `subprocess` + `ssh` directly. No paramiko dep.
- **HAProxy step** (skippable `--no-haproxy`):
  - back up `/etc/haproxy/haproxy.cfg` → `/etc/haproxy/haproxy.cfg.bak.<timestamp>` (matches existing backup convention).
  - if `backend <host>` already present (regex), skip. Else append:
    ```haproxy
    backend <host>
        option forwardfor
        http-request set-header X-Forwarded-Proto https
        server <label> <ip:port> check
    ```
  - `haproxy -c -f /etc/haproxy/haproxy.cfg` validate; restore backup + abort if invalid.
  - `systemctl reload haproxy` only on success.
- **Cert step** (skippable `--no-cert`): acme.sh stateless HTTP-01, mirroring decoded deploy pattern of existing certs:
  ```sh
  acme.sh --issue -d <host> --stateless -k ec-256 --install-cert -d <host> \
    --fullchain-file /root/.acme.sh/<host>_ecc/fullchain.cer \
    --key-file       /root/.acme.sh/<host>_ecc/<host>.key \
    --reloadcmd "cat /root/.acme.sh/<host>_ecc/fullchain.cer /root/.acme.sh/<host>_ecc/<host>.key > /etc/haproxy/certs/<host>.pem && systemctl reload haproxy"
  ```
  Idempotent: skip if `/etc/haproxy/certs/<host>.pem` valid
  (`openssl x509 -checkend 86400 -noout -in /etc/haproxy/certs/<host>.pem`).
- **`--remove`**: deletes the `backend <host>` block; leaves cert to expire.
- **DNS NOT handled by the script** — agent does it via the namecom MCP server; the SKILL.md runbook combines them.

### 1c. Skill `SKILL.md`

`.opencode/skills/add-hostname/SKILL.md`:

```yaml
---
name: add-hostname
description: Provision a new public hostname behind the home HAProxy. Creates a name.com DNS A record via the namecom MCP server, adds the HAProxy backend stanza, and issues+deploys a Let's Encrypt cert via acme.sh. Use when exposing a new subdomain on bongawonga.com, lotsof.rocks, or sso.rocks — and say "hostname" or "subdomain" or "DNS" or "HAProxy" or "cert".
---
```

Body = runbook: for `host → ip → backend ip:port`:
1. **Verify apex zone** is at name.com (MCP `ListDomains`).
2. **DNS via MCP**: `ListRecords` for apex zone → find existing A record for the host label →
   `CreateRecord` (host=label, type=A, answer=ip, ttl=300) or `UpdateRecord` (full overwrite). Apex uses `@`.
3. **Wait**: poll `socket.gethostbyname(host)` via bash until it resolves (~5 min timeout, `--no-wait` skips).
4. **HAProxy + cert**: `uv run ~/.config/opencode/skills/add-hostname/add_hostname.py --host <fqdn> --backend <ip:port> --backend-name <label>`.
5. **Verify**: `curl -sk https://<fqdn>/` returns expected content; cert is valid.
6. **Cleanup**: `--remove` for HAProxy (script), MCP `DeleteRecord` for DNS.

Documents: SNI-router topology (only `backend` stanza needed — no `frontend` edits),
`strict-sni` constraint (cert must exist before TLS — cert step precedes any client),
`loadbalancer`/`arm` SSH aliases, `mcp.dev.name.com` sandbox (`NAME_API_URL` unset) for dry runs.

---

## Part 2 — Frontend docker image (`frontend/Dockerfile`, multi-stage)

**Build stage** — `node:20-slim`:
- `npm ci`
- Generate `.env.production` from `ARG` defaults (public values from `AGENTS.md`, prod API URL):
  | ARG | default |
  |-----|---------|
  | `VITE_AUTH0_DOMAIN` | `bongawonga.us.auth0.com` |
  | `VITE_AUTH0_CLIENT_ID` | `hqvoam0pzpABmubbw2Hgq026cjctsfqP` |
  | `VITE_AUTH0_AUDIENCE` | `bongawonga-enterprises` |
  | `VITE_API_BASE_URL` | `https://orders.pizza42.bongawonga.com` |
- `npm run build`

**Serve stage** — `nginx:alpine`:
- copy `dist/` → `/usr/share/nginx/html`
- add `nginx.conf` with `try_files $uri /index.html` for SPA routes (`/`, `/cart`, `/checkout`, `/profile`), listen 80.

**`frontend/.dockerignore`**: `node_modules`, `dist`, `.env.local`, `.env.*.local`, `quickstart`, `*.log`.

---

## Part 3 — Backend docker image (`backend/Dockerfile`)

- Base `python:3.11-slim`.
- Install `uv`; `uv sync --frozen --no-dev` (prod deps only).
- **Add `gunicorn` to `pyproject.toml` dependencies** and run `uv lock` locally first (lockfile ships in image).
  Required because `app/__main__.py` calls `app.run(debug=True)` — wrong for prod.
- CMD: `gunicorn -w 4 -b 0.0.0.0:${PORT:-8000} "app:create_app()"`.
  `init_db()` runs idempotently per worker (`CREATE TABLE IF NOT EXISTS` + upsert) → multi-worker safe.
- **No `.env` in image** — secrets injected via compose `env_file`.
- Persist SQLite: bind named volume to `/app/instance` (Flask-SQLAlchemy `sqlite:///orders.db` resolves there).
- **`backend/.dockerignore`**: `.venv`, `orders.db`, `instance/`, `__pycache__`, `.env`, `.pytest_cache`.
- Backend CORS already permissive (`@cross_origin()` no args) — new origin works, no code change.

---

## Part 4 — Secrets file on arm host (10.10.0.68)

`scp` local `backend/.env` contents (Auth0, MGMT secret, `FLASK_SECRET_KEY`, `PORT`) to
`/root/pizza42/backend.env` (chmod 600) on arm. **Never** commit this / copy into image.

`backend/.env` currently holds (lines 7-8) an Auth0 MGMT client secret — flagged: must stay out of the image.

---

## Part 5 — docker-compose entries (append to `/root/docker-compose.yaml` on arm)

Free host ports confirmed (occupied: 8000/8001/8080/8087/9000): **backend → 8002**, **frontend → 8081**.

Existing file uses `version: "3"`, 2-space indent. Append (matching style):

```yaml
  pizza42-backend:
    build: /root/pizza42/backend
    image: pizza42-backend:latest
    ports:
      - "8002:8000"
    env_file:
      - /root/pizza42/backend.env
    volumes:
      - pizza42_backend_data:/app/instance
    restart: unless-stopped

  pizza42-frontend:
    build: /root/pizza42/frontend
    image: pizza42-frontend:latest
    ports:
      - "8081:80"
    restart: unless-stopped
```

Plus add `pizza42_backend_data:` to the existing top-level `volumes:` block.

---

## Part 6 — Provision the two hostnames via the new skill

Run twice (once per hostname). Agent does DNS via MCP, then calls `add_hostname.py` for HAProxy+cert:
- `pizza42.bongawonga.com` → DNS A `10.10.0.64` → backend `10.10.0.68:8081` (label `pizza42-frontend`)
- `orders.pizza42.bongawonga.com` → DNS A `10.10.0.64` → backend `10.10.0.68:8002` (label `pizza42-backend`)

(These are sections E & F of the earlier draft — now performed through the tool, not as one-off edits.)

---

## Part 7 — End-to-end verify

1. **Local pre-flight**: `cd backend && uv run pytest`; `cd frontend && npm run lint && npm test`.
2. **Deploy**: `rsync` source to `arm:/root/pizza42/{frontend,backend}`; on arm
   `cd /root && docker compose build pizza42-backend pizza42-frontend && docker compose up -d pizza42-backend pizza42-frontend`.
3. **Direct**: `curl http://10.10.0.68:8081/` (frontend HTML),
   `curl http://10.10.0.68:8002/api/menu` (backend menu JSON).
4. **Through HAProxy**: `curl https://pizza42.bongawonga.com/` and
   `curl https://orders.pizza42.bongawonga.com/api/menu` — valid cert, expected content.

---

## Build order (dependencies)

1. ~~Fix `op` perms; confirm name.com vault name (`op vault list`).~~ ✓
2. ~~Add `namecom-mcp` to `~/.config/opencode/opencode.json`.~~ ✓
3. ~~Create the `add-hostname` skill (`SKILL.md` + `add_hostname.py`, PEP 723 inline metadata — no `pyproject.toml`) under `~/.config/opencode/skills/add-hostname/`.~~ ✓
4. **Restart opencode** (MCP + skill loads — required per customize-opencode rules). **← pending user**
5. Pizza42 Dockerfiles + `.dockerignore`s; add `gunicorn` to backend `pyproject.toml` and `uv lock`; run `uv run pytest`, `npm run lint && npm test` locally.
6. `rsync` source + `scp` secrets to arm; append compose; `docker compose build && up -d`.
7. Use the new skill to provision both hostnames (**HAProxy + cert only — DNS already done**).
8. Auth0 dashboard URL additions (user).
9. End-to-end verify via `curl`.

---

## Known facts gathered during planning (don't re-research)

- **arm host (10.10.0.68)**: x86_64 (despite name), Docker 29.1.4 / Compose v5, `git`+`rsync` present, 49G free. SSH alias `arm` (root).
- **loadbalancer (10.10.0.64)**: HAProxy 3.0.11, acme.sh at `/usr/local/bin/acme.sh`, stateless HTTP-01 pattern (HAProxy `:80` serves thumbprint, certs in `/etc/haproxy/certs/*.pem`, deploy cmd = `cat fullchain.cer key > pem && systemctl reload haproxy`). SSH alias `loadbalancer` (root).
- HAProxy topology: SNI-router frontend on `:443` → TCP passthrough for PVE, else to `127.0.0.1:8443` (termination frontend with `strict-sni`). Default frontend routes by `use_backend %[req.hdr(Host),lower]` → **only a `backend <host>` stanza is needed** to add a site (no frontend edit). But `strict-sni` means cert pem must exist before TLS works → cert before client.
- Existing compose services on arm: pgdb1, ghost-db, ghost-timothy, oracle-sp/2, wg-easy, oaa-training-api (8001), bifrost (8087), plus standalone portainer (9000), arm-rippers (8080), timetracker (8000), veza-insight (6061).
- name.com MCP uses **Core API v1** (not legacy v4 the `namecom` PyPI wraps). Has tools for List/Create/Update/Delete Record. Apex A record host = `@`.
- `frontend/.env.local` currently: `VITE_API_BASE_URL=http://127.0.0.1:8000` (dev) — prod override via build-arg.
- `backend/.env` contains a hardcoded Auth0 MGMT secret (lines 7-8) — must NOT enter the image; inject via compose env_file.
- 1Password: item `Name.com`, fields `username` and `api_token`. Vault name **Private**.
- opencode skill format: frontmatter `name`+`description` required; file at `~/.config/opencode/skills/add-hostname/SKILL.md`. MCP block in `opencode.json` uses `{env:VAR}` and `{file:path}` interpolation. Config changes need opencode restart.