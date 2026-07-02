import pytest
from unittest.mock import patch

from app import create_app


def test_mysql_uri_sets_ssl_config():
    """MySQL URIs should configure SSL with check_hostname=False."""
    with patch('app.init_db'):
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://user:pass@host:3306/db",
            "TESTING": True,
        })
        
        engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        connect_args = engine_options.get("connect_args", {})
        ssl_config = connect_args.get("ssl", {})
        
        assert "ssl" in connect_args
        assert ssl_config.get("check_hostname") is False


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


def test_ssl_config_uses_pymysql_format():
    """SSL config should use PyMySQL's ssl dict format, not ssl_mode."""
    with patch('app.init_db'):
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://user:pass@host:3306/db",
            "TESTING": True,
        })
        
        engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        connect_args = engine_options.get("connect_args", {})
        
        assert "ssl_mode" not in connect_args
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], dict)


def test_ssl_config_is_truthy_dict():
    """SSL config dict must be truthy for PyMySQL to enable SSL."""
    with patch('app.init_db'):
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://user:pass@host:3306/db",
            "TESTING": True,
        })
        
        engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        connect_args = engine_options.get("connect_args", {})
        ssl_config = connect_args.get("ssl", {})
        
        assert bool(ssl_config), "SSL config dict must be truthy (non-empty)"
