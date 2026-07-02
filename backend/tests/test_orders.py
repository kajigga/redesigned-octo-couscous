import pytest


def _mock_auth(monkeypatch, sub="auth0|testuser", scope="pizza42-order"):
    """Bypass JWT verification and set the given sub/scope for testing."""
    current = {"sub": sub, "scope": scope}

    def mock_verify():
        from flask import g

        g._jwt_extended_jwt = dict(current)

    monkeypatch.setattr("app.auth.verify_jwt_in_request", mock_verify)
    return current


def test_401_without_token(client):
    """POST /api/orders returns 401 when no token is provided."""
    resp = client.post("/api/orders", json={"items": [{"id": "pepperoni", "quantity": 1}]})
    assert resp.status_code == 401


def test_401_without_token_get(client):
    """GET /api/orders returns 401 when no token is provided."""
    resp = client.get("/api/orders")
    assert resp.status_code == 401


def test_403_no_scope(client, monkeypatch):
    """POST /api/orders returns 403 when token lacks the required scope."""
    _mock_auth(monkeypatch, scope="wrong-scope")
    resp = client.post(
        "/api/orders",
        json={"items": [{"id": "pepperoni", "quantity": 1}], "address": {"name": "T"}},
    )
    assert resp.status_code == 403


def test_unknown_item_400(client, monkeypatch):
    """POST /api/orders returns 400 when an item ID is not in the menu."""
    _mock_auth(monkeypatch)
    resp = client.post(
        "/api/orders",
        json={
            "items": [{"id": "nonexistent", "quantity": 1}],
            "address": {"name": "T", "street": "1", "city": "C", "zip": "Z"},
        },
    )
    assert resp.status_code == 400
    assert "unknown item" in resp.get_json()["error"].lower()


def test_empty_items_400(client, monkeypatch):
    """POST /api/orders returns 400 when items array is empty."""
    _mock_auth(monkeypatch)
    resp = client.post(
        "/api/orders",
        json={"items": [], "address": {"name": "T"}},
    )
    assert resp.status_code == 400


def test_missing_body_400(client, monkeypatch):
    """POST /api/orders returns 400 when body is not valid JSON."""
    _mock_auth(monkeypatch)
    resp = client.post("/api/orders", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_post_computes_total_from_menu(client, monkeypatch):
    """POST /api/orders ignores client-sent total and computes it server-side."""
    _mock_auth(monkeypatch)
    resp = client.post(
        "/api/orders",
        json={
            "items": [
                {"id": "pepperoni", "quantity": 2},
                {"id": "hawaiian", "quantity": 1},
            ],
            "total": 999,
            "address": {"name": "Kevin", "street": "1 Oak", "city": "NYC", "zip": "10001"},
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["total"] == pytest.approx(2 * 12.99 + 11.99)
    assert data["total"] != 999
    assert data["status"] == "received"
    assert data["id"].startswith("ORD-")
    assert data["address"]["name"] == "Kevin"
    assert len(data["items"]) == 2


def test_get_returns_only_callers_orders(client, monkeypatch):
    """GET /api/orders only returns orders for the authenticated user."""
    current = _mock_auth(monkeypatch, sub="auth0|user1")

    client.post(
        "/api/orders",
        json={
            "items": [{"id": "pepperoni", "quantity": 1}],
            "address": {"name": "User1", "street": "1", "city": "C", "zip": "Z"},
        },
    )

    current["sub"] = "auth0|user2"
    client.post(
        "/api/orders",
        json={
            "items": [{"id": "sausage", "quantity": 2}],
            "address": {"name": "User2", "street": "2", "city": "C", "zip": "Z"},
        },
    )

    current["sub"] = "auth0|user1"
    resp = client.get("/api/orders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["orders"]) == 1
    assert data["orders"][0]["address"]["name"] == "User1"

    current["sub"] = "auth0|user2"
    resp = client.get("/api/orders")
    assert len(resp.get_json()["orders"]) == 1
    assert resp.get_json()["orders"][0]["address"]["name"] == "User2"


def test_get_orders_shape(client, monkeypatch):
    """GET /api/orders response matches the shape of a created order."""
    _mock_auth(monkeypatch)
    resp = client.post(
        "/api/orders",
        json={
            "items": [{"id": "pepperoni", "quantity": 1}],
            "address": {"name": "Alice", "street": "1", "city": "C", "zip": "Z"},
        },
    )
    order = resp.get_json()

    resp = client.get("/api/orders")
    data = resp.get_json()
    assert len(data["orders"]) == 1
    got = data["orders"][0]
    assert got["id"] == order["id"]
    assert got["total"] == order["total"]
    assert got["status"] == "received"
    assert got["items"] == order["items"]
    assert got["address"] == order["address"]
