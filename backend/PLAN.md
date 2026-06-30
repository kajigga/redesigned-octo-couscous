# Pizza42 Backend — Implementation Plan

Build a simple Flask backend in `../backend` that lets authenticated users POST a pizza
order and GET their current orders. Auth via Auth0 OAuth2 access tokens (RS256/JWKS).
Menu/inventory is served by the API from a SQLite `menu` table. Run with `uv` (no manual
venv). **Backend only** — frontend wiring is a separate follow-up.

## Stack

- **Flask** + `flask-jwt-extended` (RS256 via JWKS) + `PyJWT`
- **SQLite** (stdlib `sqlite3`, file `orders.db`)
- **uv** for project/dep management and running — no manual venv
- Dev entry: **`uv run python -m app`**
- Auth0: domain `bongawonga.us.auth0.com`, audience `bongawonga-enterprises`, scope `pizza42-order`
- Issuer: `https://bongawonga.us.auth0.com/`; JWKS: `…/.well-known/jwks.json`

## File structure

```
backend/
  pyproject.toml          # uv project, deps, optional pytest
  .env.example
  .gitignore              # orders.db, .venv, __pycache__, .env
  README.md               # uv setup + run/test commands
  app/
    __init__.py           # create_app() factory
    __main__.py           # python -m app entry -> app.run()
    config.py             # env via python-dotenv
    auth.py               # JWKS decode_key_callback + @require_scope
    db.py                 # sqlite connection + schema bootstrap + menu seed
    routes/
      menu.py             # GET /api/menu (public)
      orders.py           # POST/GET /api/orders (auth)
  tests/
    test_menu.py
    test_orders.py
```

## pyproject.toml

```toml
[project]
name = "pizza42-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "flask>=3.0",
  "flask-jwt-extended>=4.6",
  "pyjwt>=2.8",
  "python-dotenv>=1.0",
]
[project.optional-dependencies]
dev = ["pytest>=8"]
```

- Install deps: `uv sync` (creates `.venv` automatically)
- Run dev server: `uv run python -m app`
- Run tests: `uv run pytest`
- Add a dep: `uv add <pkg>`

## SQLite schema (`app/db.py`)

```sql
CREATE TABLE IF NOT EXISTS menu (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, price REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL, date TEXT NOT NULL,
  total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'received',
  address_name TEXT, street TEXT, city TEXT, zip TEXT
);
CREATE TABLE IF NOT EXISTS order_items (
  order_id TEXT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  item_id TEXT NOT NULL REFERENCES menu(id),
  name TEXT NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL,
  PRIMARY KEY (order_id, item_id)
);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
```

On startup, seed `menu` idempotently (upsert) with the 3 pizzas mirroring
`frontend/src/data/menu.js`:

| id        | name      | price  |
|-----------|-----------|--------|
| pepperoni | Pepperoni | 12.99  |
| sausage   | Sausage   | 13.99  |
| hawaiian  | Hawaiian  | 11.99  |

## Endpoints

### GET /api/menu — public (no auth)

Returns `[{id, name, description, price}, …]`. Becomes the canonical inventory source the
frontend can fetch later (follow-up to wire it into `src/data/menu.js`).

### POST /api/orders — `@jwt_required` + `@require_scope("pizza42-order")`

Accepts the frontend payload (matches `frontend/src/api/orders.js` +
`frontend/src/routes/Checkout.jsx:74`):

```json
{
  "items": [{"id": "pepperoni", "quantity": 2}],
  "total": 25.98,
  "address": {"name": "Kevin", "street": "…", "city": "…", "zip": "…"}
}
```

- Validate every `item.id` exists in `menu` → 400 if unknown (FK also enforces).
- **Server-authoritative total**: compute from `menu` prices (snapshot price into
  `order_items.price`), ignore client-sent `total`.
- Generate `id = "ORD-" + uuid4().hex[:8]`, `date = datetime.now(timezone.utc).isoformat()`,
  `status = "received"`, `user_id = get_jwt()["sub"]`.
- Return the order in the shape the frontend already expects (matches
  `frontend/src/mocks/orders.js`):

```json
{
  "id": "ORD-…",
  "date": "…",
  "items": [{"id": "pepperoni", "name": "Pepperoni", "quantity": 2, "price": 12.99}],
  "total": 25.98,
  "status": "received",
  "address": {"name": "…", "street": "…", "city": "…", "zip": "…"}
}
```

### GET /api/orders — `@jwt_required` + `@require_scope("pizza42-order")`

Returns `{"orders": [<same order shape>, …]}` for `get_jwt()["sub"]`, newest first.
(Frontend doesn't call this yet — `Profile.jsx` currently reads the Auth0
`pizza42/orders` claim or falls back to mocks. Wiring this endpoint is a follow-up.)

## Auth (`app/auth.py`)

`flask-jwt-extended` with `JWT_ALGORITHM=RS256`, `JWT_AUDIENCE=bongawonga-enterprises`,
`JWT_ISSUER=https://bongawonga.us.auth0.com/`. `@jwt_manager.decode_key_callback` uses
`PyJWKClient(AUTH0_DOMAIN + "/.well-known/jwks.json")` to resolve the signing key by JWT
header `kid` (handles key rotation). A `@require_scope` decorator checks
`get_jwt()["scope"]` for `pizza42-order` (403 if missing).

## .env.example

```
AUTH0_DOMAIN=bongawonga.us.auth0.com
AUTH0_AUDIENCE=bongawonga-enterprises
AUTH0_SCOPE=pizza42-order
FLASK_SECRET_KEY=change-me
PORT=8000
```

## Tests (`uv run pytest`)

Monkeypatch JWT decode to inject a synthetic `sub` (no real Auth0 keys needed offline).

- `test_menu.py`: GET /api/menu returns 3 pizzas, no token required.
- `test_orders.py`:
  - 401 without token
  - 403 valid-but-no-scope
  - unknown item id → 400
  - POST recomputes total from menu
  - GET returns only the caller's orders

## Out of scope (explicit)

- Frontend wiring (`client.js` BASE_URL → `http://localhost:8000`, fetching `/api/menu`,
  adding the GET /api/orders call in Profile, removing mock fallback) — separate follow-up.
- Production WSGI server, migrations (schema bootstrap only).
- `AGENTS.md` for the backend repo — add once the backend exists.

## Frontend context (for reference; do NOT edit frontend in this task)

- `frontend/src/api/client.js` posts to `https://orders.bongawonga.com` with
  `Authorization: Bearer <token>`, JSON body.
- `.env.local`: domain `bongawonga.us.auth0.com`, audience `bongawonga-enterpires`,
  client id `hqvoam0pzpABmubbw2Hgq026cjctsfqP`, port 5173.
- Order payload sent by `Checkout.jsx`: `{items:[{id,quantity}], total, address:{name,street,city,zip}}`.
- Required scope asserted by frontend: `pizza42-order` (see `Checkout.jsx:9`).