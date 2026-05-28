from jose import jwt
from jose.exceptions import JWTError

SECRET_KEY = "temporary"


def decode_token(token: str):
    try:
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError:
        return None
