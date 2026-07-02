import json
import time
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app


_mgmt_token = None
_mgmt_token_expires = 0.0


def _get_mgmt_token():
    global _mgmt_token, _mgmt_token_expires

    now = time.time()
    if _mgmt_token and now < _mgmt_token_expires - 60:
        return _mgmt_token

    client_id = current_app.config.get("AUTH0_MGMT_CLIENT_ID")
    client_secret = current_app.config.get("AUTH0_MGMT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("AUTH0_MGMT_CLIENT_ID / AUTH0_MGMT_CLIENT_SECRET not configured")

    domain = current_app.config.get("AUTH0_DOMAIN", "bongawonga.us.auth0.com")
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": f"https://{domain}/api/v2/",
        "grant_type": "client_credentials",
    }).encode()

    req = urllib.request.Request(
        f"https://{domain}/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
            _mgmt_token = body["access_token"]
            _mgmt_token_expires = now + body.get("expires_in", 86400)
            return _mgmt_token
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to get Auth0 Management API token: {e}") from e


def add_order_to_app_metadata(user_id, order_data):
    token = _get_mgmt_token()
    domain = current_app.config.get("AUTH0_DOMAIN", "bongawonga.us.auth0.com")
    base = f"https://{domain}/api/v2/users/{urllib.parse.quote(user_id, safe='')}"

    req_get = urllib.request.Request(
        base,
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req_get) as resp:
            user_body = json.loads(resp.read())
    except urllib.error.URLError as e:
        current_app.logger.warning("Failed to read user %s: %s", user_id, e)
        return

    app_metadata = user_body.get("app_metadata") or {}
    orders = app_metadata.get("pizza42/orders") or []
    orders.append(order_data)
    app_metadata["pizza42/orders"] = orders

    payload = json.dumps({"app_metadata": app_metadata}).encode()
    req_patch = urllib.request.Request(
        base,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    try:
        urllib.request.urlopen(req_patch)
    except urllib.error.URLError as e:
        current_app.logger.warning("Failed to patch user %s: %s", user_id, e)
