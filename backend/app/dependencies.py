from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import SESSION_COOKIE_NAME, read_session_cookie
from app.database import get_db
from app.models.user import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = read_session_cookie(request.cookies.get(SESSION_COOKIE_NAME))
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user


async def get_current_user_from_cookie_value(db: AsyncSession, cookie_value: str | None) -> User | None:
    """Used by the WebSocket endpoint, which reads cookies differently than HTTP requests."""
    user_id = read_session_cookie(cookie_value)
    if user_id is None:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
