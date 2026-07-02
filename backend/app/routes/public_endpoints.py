import os

from flask import Blueprint
from flask_cors import cross_origin

from ..cache import cache
from ..models import MenuItem

public_bp = Blueprint("public", __name__)


@public_bp.route("/menu")
@cross_origin()
@cache(ttl_seconds=300)
def get_menu():
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


@public_bp.route("/version")
@cross_origin()
def get_version():
    return {"version": os.environ.get("GIT_SHA") or os.environ.get("RENDER_GIT_COMMIT", "unknown")}
