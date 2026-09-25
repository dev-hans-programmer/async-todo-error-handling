# Authorisation: Bearer <token>
# 1. We will have extract the token from this entire request header
# We will have to see whether the token is valid, if valid extract the claims
# We will also have to check whether the user actually exists in our system

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.repo.user_repo import UserRepository
from app.security import decode_access_token

bearer = HTTPBearer()


# credentials -> the actual token data
async def get_current_user(credentials:Annotated[HTTPAuthorizationCredentials, Depends(bearer)], db: Annotated[AsyncSession, Depends(get_db)]):
    token = credentials.credentials


    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        claims: dict[str,Any ] = decode_access_token(token)

        print(claims)

        user_id: str = claims.get("sub")
    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=f"Not authenticated {str(e)}")

    
    user = await UserRepository(db).get_by_id(int(user_id))

    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # assignment 2: 
    # We can have more checks
    # You can have a flag in your user model i.e is_active
    # password change: 
    password_changed_at = user.password_changed_at

    if password_changed_at is not None:
        token_issued_at = datetime.fromtimestamp(claims['iat'],tz=UTC)

        if token_issued_at <= password_changed_at:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Not authenticated:password changed")

    # JWKS URI
    # OIDC client
    # Oauth

    return user




CurrentUser = Annotated[User, Depends(get_current_user)]
