import sqlite3

from flask import current_app, g

# Seed data mirrors frontend/src/data/menu.js — keep in sync.
MENU_SEED = [
    ("pepperoni", "Pepperoni", "Classic pepperoni with mozzarella cheese", 12.99),
    ("sausage", "Sausage", "Italian sausage with mozzarella cheese", 13.99),
    ("hawaiian", "Hawaiian", "Ham and pineapple with mozzarella cheese", 11.99),
]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS menu (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  description TEXT,
  price       REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
  id           TEXT PRIMARY KEY,
  user_id      TEXT NOT NULL,
  date         TEXT NOT NULL,
  total        REAL NOT NULL,
  status       TEXT NOT NULL DEFAULT 'received',
  address_name TEXT,
  street       TEXT,
  city         TEXT,
  zip          TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
  order_id TEXT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  item_id  TEXT NOT NULL REFERENCES menu(id),
  name     TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  price    REAL NOT NULL,
  PRIMARY KEY (order_id, item_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(_SCHEMA)
    db.executemany(
        "INSERT INTO menu (id, name, description, price) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET name=excluded.name, "
        "description=excluded.description, price=excluded.price",
        MENU_SEED,
    )
    db.commit()


def get_menu_row(db, item_id):
    return db.execute("SELECT * FROM menu WHERE id = ?", (item_id,)).fetchone()


def insert_order(db, order_id, user_id, date, total, address, items):
    db.execute(
        "INSERT INTO orders (id, user_id, date, total, status, "
        "address_name, street, city, zip) VALUES (?, ?, ?, ?, 'received', ?, ?, ?, ?)",
        (
            order_id,
            user_id,
            date,
            total,
            address.get("name"),
            address.get("street"),
            address.get("city"),
            address.get("zip"),
        ),
    )
    db.executemany(
        "INSERT INTO order_items (order_id, item_id, name, quantity, price) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            (order_id, item["id"], item["name"], item["quantity"], item["price"])
            for item in items
        ],
    )
    db.commit()


def fetch_orders_for_user(db, user_id):
    rows = db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY date DESC", (user_id,)
    ).fetchall()
    result = []
    for row in rows:
        item_rows = db.execute(
            "SELECT item_id AS id, name, quantity, price FROM order_items "
            "WHERE order_id = ?",
            (row["id"],),
        ).fetchall()
        result.append(
            {
                "id": row["id"],
                "date": row["date"],
                "items": [dict(ir) for ir in item_rows],
                "total": row["total"],
                "status": row["status"],
                "address": {
                    "name": row["address_name"],
                    "street": row["street"],
                    "city": row["city"],
                    "zip": row["zip"],
                },
            }
        )
    return result