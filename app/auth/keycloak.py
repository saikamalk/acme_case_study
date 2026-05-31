import os
import time
from typing import Any, Dict

import requests
from jose import jwt
from jose.exceptions import JWTError

KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://keycloak:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "acme")
KEYCLOAK_ISSUER = os.getenv(
    "KEYCLOAK_ISSUER",
    f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}",
)
# Optional. Set this if you want audience validation.
# For your realm-export, this can be "acme-api".
KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_AUDIENCE", "").strip() or None
JWKS_TTL_SECONDS = 300
_JWKS_CACHE: dict[str, Any] = {
    "fetched_at": 0.0,
    "keys": None,
}


def _openid_config_url() -> str:
    return f"{KEYCLOAK_ISSUER}/.well-known/openid-configuration"


def _fetch_jwks_uri() -> str:
    resp = requests.get(_openid_config_url(), timeout=5)
    resp.raise_for_status()
    data = resp.json()
    jwks_uri = data.get("jwks_uri")
    if not jwks_uri:
        raise JWTError("Keycloak discovery document did not contain jwks_uri")
    return jwks_uri


def _fetch_jwks(force_refresh: bool = False) -> Dict[str, Any]:
    now = time.time()
    if (
            not force_refresh
            and _JWKS_CACHE["keys"] is not None
            and (now - float(_JWKS_CACHE["fetched_at"])) < JWKS_TTL_SECONDS
    ):
        return _JWKS_CACHE["keys"]
    jwks_uri = _fetch_jwks_uri()
    resp = requests.get(jwks_uri, timeout=5)
    resp.raise_for_status()
    jwks = resp.json()
    _JWKS_CACHE["keys"] = jwks
    _JWKS_CACHE["fetched_at"] = now
    return jwks


def _get_signing_key(token: str) -> Dict[str, Any]:
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise JWTError("Token header missing kid")
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    # One retry in case key rotation happened
    jwks = _fetch_jwks(force_refresh=True)
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise JWTError("Signing key not found in JWKS")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Verify signature + exp + issuer, and optionally audience.
    Returns verified claims.
    """
    signing_key = _get_signing_key(token)
    options = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_iat": True,
        "verify_nbf": True,
        "verify_aud": KEYCLOAK_AUDIENCE is not None,
    }
    try:
        return jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            audience=KEYCLOAK_AUDIENCE,
            options=options,
        )
    except JWTError:
        raise
