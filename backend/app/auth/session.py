from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.config import get_settings

SESSION_COOKIE_NAME = "todo_session"
SESSION_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days


def _serializer() -> URLSafeTimedSerializer:
    settings = get_settings()
    return URLSafeTimedSerializer(settings.session_secret, salt="todo-session")


def create_session_cookie(user_id: int) -> str:
    return _serializer().dumps({"user_id": user_id})


def read_session_cookie(value: str | None) -> int | None:
    if not value:
        return None
    try:
        data = _serializer().loads(value, max_age=SESSION_MAX_AGE_SECONDS)
    except BadSignature:
        return None
    user_id = data.get("user_id")
    return int(user_id) if user_id is not None else None
