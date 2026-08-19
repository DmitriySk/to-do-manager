from authlib.integrations.starlette_client import OAuth

from app.config import get_settings

settings = get_settings()

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)


async def fetch_github_profile(token: dict) -> dict:
    client = oauth.create_client("github")
    user_resp = await client.get("user", token=token)
    user_resp.raise_for_status()
    profile = user_resp.json()

    email = profile.get("email")
    if not email:
        emails_resp = await client.get("user/emails", token=token)
        if emails_resp.status_code == 200:
            emails = emails_resp.json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = (primary or (emails[0] if emails else {})).get("email")

    return {
        "provider_user_id": str(profile["id"]),
        "email": email,
        "display_name": profile.get("name") or profile.get("login"),
        "avatar_url": profile.get("avatar_url"),
    }


def parse_google_profile(userinfo: dict) -> dict:
    return {
        "provider_user_id": userinfo["sub"],
        "email": userinfo.get("email"),
        "display_name": userinfo.get("name") or userinfo.get("email") or "Google User",
        "avatar_url": userinfo.get("picture"),
    }
