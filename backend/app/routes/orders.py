from uuid import uuid4
from datetime import datetime, timezone

from flask import Blueprint, current_app, request
from flask_cors import cross_origin
from flask_jwt_extended import get_jwt

from ..extensions import db
from ..auth import is_authenticated
from ..models import MenuItem
from ..db import insert_order, fetch_orders_for_user, resolve_order_items
from ..auth0_mgmt import add_order_to_app_metadata
from ..config import Config

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/orders", methods=["POST", "OPTIONS"])
@cross_origin()
@is_authenticated(Config.AUTH0_SCOPE)
def create_order():
    """Create a new order (auth required, scope pizza42-order)."""
    data = request.get_json(silent=True)
    if not data:
        return {"error": "request body required"}, 400

    items = data.get("items")
    if not items or not isinstance(items, list):
        return {"error": "items must be a non-empty array"}, 400

    resolved = resolve_order_items(items)
    if isinstance(resolved, tuple):
        return resolved

    total = round(sum(it["price"] * it["quantity"] for it in resolved), 2)
    order_id = "ORD-" + uuid4().hex[:8]
    date = datetime.now(timezone.utc).isoformat()
    address = data.get("address", {})
    user_id = get_jwt()["sub"]

    insert_order(order_id, user_id, date, total, address, resolved)

    try:
        add_order_to_app_metadata(
            user_id,
            {
                "id": order_id,
                "date": date,
                "items": resolved,
                "total": total,
                "status": "received",
                "address": address,
            },
        )
    except Exception as exc:
        current_app.logger.warning("Failed to update Auth0 app_metadata: %s", exc)

    return {
        "id": order_id,
        "date": date,
        "items": resolved,
        "total": total,
        "status": "received",
        "address": address,
    }, 201


@orders_bp.route("/orders", methods=["GET"])
@cross_origin()
@is_authenticated
def list_orders():
    """List the authenticated user's orders."""
    user_id = get_jwt()["sub"]
    orders = fetch_orders_for_user(user_id)
    return {"orders": orders}
