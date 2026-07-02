from flask import Blueprint
from flask_cors import cross_origin

from ..cache import cache
from ..models import MenuItem

menu_bp = Blueprint("menu", __name__)


@menu_bp.route("/menu")
@cross_origin()
@cache(ttl_seconds=300)
def get_menu():
    """Return the full menu (public, no auth required, cached for 5 min)."""
    items = MenuItem.query.all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "imageUrl": item.image_url,
        }
        for item in items
    ]
