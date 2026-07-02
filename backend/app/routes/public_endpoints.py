import os
from importlib.metadata import version as get_pkg_version

from flask import Blueprint, make_response
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
    try:
        semver = get_pkg_version("pizza42-backend")
    except Exception:
        semver = "unknown"
    response = make_response({
        "version": semver,
        "gitSha": os.environ.get("GIT_SHA") or os.environ.get("RENDER_GIT_COMMIT", "unknown"),
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
