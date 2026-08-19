from pydantic import BaseModel, Field


class TestLoginRequest(BaseModel):
    provider: str = Field(pattern="^(google|github)$")
    provider_user_id: str
    email: str | None = None
    display_name: str
    avatar_url: str | None = None
