from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.routers import auth, lists, tasks
from app.websocket import router as websocket

settings = get_settings()

app = FastAPI(title="Personal To-Do Manager API")

# Used only by Authlib to store the OAuth "state" nonce during the redirect
# round-trip. Distinct from our own application session cookie (see
# app/auth/session.py), which is what actually authenticates API/WS requests.
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, same_site="lax")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(lists.router)
app.include_router(tasks.router)
app.include_router(websocket.router)

if settings.enable_dev_endpoints:
    from app.routers import dev

    app.include_router(dev.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
