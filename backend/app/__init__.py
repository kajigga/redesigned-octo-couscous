import logging
from flask import Flask

from .config import Config
from .extensions import db as _db
from . import models
from .db import init_db
from .auth import jwt_manager
from .routes.public_endpoints import public_bp
from .routes.orders import orders_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.config["JWT_ALGORITHM"] = "RS256"
    app.config["JWT_DECODE_ALGORITHMS"] = ["RS256"]
    app.config["JWT_AUDIENCE"] = Config.AUTH0_AUDIENCE
    app.config["JWT_ISSUER"] = Config.AUTH0_ISSUER

    _db.init_app(app)
    jwt_manager.init_app(app)

    with app.app_context():
        init_db()

    app.register_blueprint(public_bp, url_prefix="/api")
    app.register_blueprint(public_bp, url_prefix="/", name='default')
    app.register_blueprint(orders_bp, url_prefix="/api")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Ensure database sessions are cleaned up after each request."""
        if exception:
            _db.session.rollback()
        _db.session.remove()

    return app
