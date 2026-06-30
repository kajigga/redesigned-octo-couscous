import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "bongawonga.us.auth0.com")
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "bongawonga-enterprises")
    AUTH0_SCOPE = os.environ.get("AUTH0_SCOPE", "pizza42-order")
    AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"
    AUTH0_JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-me")
    PORT = int(os.environ.get("PORT", "8000"))
    DATABASE = os.environ.get("DATABASE", "orders.db")