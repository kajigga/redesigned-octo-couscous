import pytest
from unittest.mock import patch

from app import create_app


def test_postgresql_uri_no_extra_config():
    """PostgreSQL URIs should not require extra engine configuration."""
    with patch('app.init_db'):
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg://user:pass@host:5432/db",
            "TESTING": True,
        })
        
        engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        assert not engine_options, "PostgreSQL should not need extra engine options"


def test_postgresql_with_sslmode():
    """PostgreSQL URIs with sslmode should work without extra config."""
    with patch('app.init_db'):
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg://user:pass@host:5432/db?sslmode=require",
            "TESTING": True,
        })
        
        assert app.config.get("SQLALCHEMY_DATABASE_URI").startswith("postgresql+psycopg://")


def test_sqlite_uri_no_ssl_config():
    """SQLite URIs should not configure SSL."""
    with patch('app.init_db'):
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
            "TESTING": True,
        })
        
        engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        connect_args = engine_options.get("connect_args", {})
        
        assert "ssl" not in connect_args
