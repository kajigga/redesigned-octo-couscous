import os
import tempfile

import pytest

from app import create_app


@pytest.fixture
def app():
    """Flask app backed by a temporary SQLite database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })
    yield application
    with application.app_context():
        application.extensions["sqlalchemy"].engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Test client for the Flask app."""
    return app.test_client()
