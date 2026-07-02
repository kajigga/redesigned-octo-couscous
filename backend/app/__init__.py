from flask import Flask

from .config import Config
from .extensions import db as _db
from . import models
from .db import init_db
from .auth import jwt_manager
from .routes.public_endpoints import public_bp
from .routes.orders import orders_bp


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("mysql"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"ssl": {"ssl-mode": "REQUIRED"}}
        }

    app.config["JWT_ALGORITHM"] = "RS256"
    app.config["JWT_DECODE_ALGORITHMS"] = ["RS256"]
    app.config["JWT_AUDIENCE"] = Config.AUTH0_AUDIENCE
    app.config["JWT_ISSUER"] = Config.AUTH0_ISSUER

    _db.init_app(app)
    jwt_manager.init_app(app)

    with app.app_context():
        init_db()

    app.register_blueprint(public_bp, url_prefix="/api")
    app.register_blueprint(orders_bp, url_prefix="/api")

    return app
