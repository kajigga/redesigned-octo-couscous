from functools import wraps

import jwt
from flask import current_app
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request

jwt_manager = JWTManager()


@jwt_manager.decode_key_loader
def decode_key_loader(jwt_header, jwt_payload):
    """Resolve the RS256 signing key from Auth0 JWKS."""
    jwks_client = jwt.PyJWKClient(current_app.config["AUTH0_JWKS_URL"])
    signing_key = jwks_client.get_signing_key(jwt_header["kid"])
    return signing_key.key


def is_authenticated(scope=None):
    """Decorator that optionally enforces a required Auth0 scope on an endpoint.
    When called without arguments (``@is_authenticated``), it verifies the user is
    authenticated but does not check scope.  When called with a scope string
    (``@is_authenticated("pizza42-order")``), it also validates the scope.
    """

    if callable(scope):
        # Used as bare @is_authenticated (no parentheses / call)
        fn = scope
        scope = None

        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            return fn(*args, **kwargs)

        return wrapper

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if scope is not None:
                claims = get_jwt()
                token_scope = claims.get("scope", "")
                if scope not in token_scope.split():
                    return {"error": "insufficient_scope"}, 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
