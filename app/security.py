from typing import Any

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

from datetime import UTC, datetime, timedelta

import jwt

from app.config_settings.settings import settings


def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(password:str, hashed_password: str):
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int):
    # header
    # payload
    # signature
    # Secret we need
    # Symmetric(HS256) and another is Asymmetric(RS256)
    # HS256 -> We use same secret to create the token and also verify the token
    # RS256 -> We need 2 types of secrets i.e private secret and public secret
    # private secret is used to create the token: We will have to keep this secret secure
    # public secret is used to verify the token

    # Some predefined names we can use while creating the payload
    # sub, iat, exp, aud,
    # you can also use your custom claims

    now = datetime.now(UTC)

    # we call them access token which expires in short span of time
    # refresh token: This token is used to rotate an access token

    # This payload is also called claims
    # in the token, we never put any sensitive information cause token payload could be extracted normally
    # But we use verification in our codebase to actually understand whether the token is valid
    payload: dict[str,Any ] = {
        "sub": str(user_id),
        # "aud":"todo-client",
        "iat":now,
        "exp":now + timedelta(seconds=30*60) # after 15 mins the same token will fail to verify
    }

    # the client has to send a header named Authorisation which will contain the token:
    # Authorisation: Bearer <token>
    # we will have to have a way to verify the token

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def decode_access_token(token: str):
    # verify the token
    # this method verifies your expiration time as well
    return jwt.decode(token, settings.JWT_SECRET,algorithms=["HS256"] )






