from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.oauth import fetch_github_profile, oauth, parse_google_profile
from app.auth.session import SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS, create_session_cookie
from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import TestLoginRequest
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_session_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_cookie(user_id),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,  # set True when served over HTTPS in production
        path="/",
    )


async def _upsert_user(db: AsyncSession, provider: str, profile: dict) -> User:
    result = await db.execute(
        select(User).where(User.provider == provider, User.provider_user_id == profile["provider_user_id"])
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            provider=provider,
            provider_user_id=profile["provider_user_id"],
            email=profile.get("email"),
            display_name=profile["display_name"],
            avatar_url=profile.get("avatar_url"),
        )
        db.add(user)
    else:
        user.email = profile.get("email") or user.email
        user.display_name = profile["display_name"]
        user.avatar_url = profile.get("avatar_url") or user.avatar_url

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider not in ("google", "github"):
        raise HTTPException(status_code=404, detail="Unknown provider")
    client = oauth.create_client(provider)
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}", name="oauth_callback")
async def oauth_callback(provider: str, request: Request, db: AsyncSession = Depends(get_db)):
    if provider not in ("google", "github"):
        raise HTTPException(status_code=404, detail="Unknown provider")

    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)

    if provider == "google":
        userinfo = token.get("userinfo") or await client.userinfo(token=token)
        profile = parse_google_profile(userinfo)
    else:
        profile = await fetch_github_profile(token)

    user = await _upsert_user(db, provider, profile)

    response = RedirectResponse(url=settings.frontend_url)
    _set_session_cookie(response, user.id)
    return response


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


if settings.enable_test_auth:

    @router.post("/test-login", response_model=UserOut, status_code=status.HTTP_200_OK)
    async def test_login(payload: TestLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
        """Mocks an SSO provider's response so the test suite can exercise the
        login success path without contacting Google/GitHub. Only registered
        when ENABLE_TEST_AUTH=true (never enabled in a normal run)."""
        user = await _upsert_user(
            db,
            payload.provider,
            {
                "provider_user_id": payload.provider_user_id,
                "email": payload.email,
                "display_name": payload.display_name,
                "avatar_url": payload.avatar_url,
            },
        )
        _set_session_cookie(response, user.id)
        return user
