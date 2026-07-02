import os
from importlib.metadata import version as get_pkg_version

from flask import Blueprint, jsonify, make_response
from flask_cors import cross_origin

from ..cache import cache
from ..extensions import db
from ..models import MenuItem

public_bp = Blueprint("public", __name__)


@public_bp.route("/menu")
@cross_origin()
@cache(ttl_seconds=300)
def get_menu():
    """Return all menu items."""
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
    """Return the app version and git SHA."""
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

@public_bp.route("/")
@cross_origin()
def api_home():
    """Serve the API root, returning version info."""
    return get_version()


@public_bp.route("/health")
@cross_origin()
def health_check():
    """Check database connectivity and return health status."""
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 503
