def test_menu_returns_all_pizzas(client):
    """All three seeded pizzas returned with correct shape."""
    resp = client.get("/api/menu")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 3

    ids = {item["id"] for item in data}
    assert ids == {"pepperoni", "sausage", "hawaiian"}

    for item in data:
        assert "name" in item
        assert "description" in item
        assert "price" in item
        assert isinstance(item["price"], float)


def test_menu_no_auth_required(client):
    """Menu is accessible without authentication."""
    resp = client.get("/api/menu")
    assert resp.status_code == 200
