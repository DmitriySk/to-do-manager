import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.session import SESSION_COOKIE_NAME
from app.database import SessionLocal
from app.dependencies import get_current_user_from_cookie_value
from app.models.user import User
from app.websocket.manager import ConnectionState
from app.websocket.notifier import compute_notifications

router = APIRouter()


async def _send_batch(websocket: WebSocket, state: ConnectionState, user: User) -> None:
    async with SessionLocal() as db:
        notifications = await compute_notifications(db, user, enabled_types=state.enabled_types)
    visible = [n for n in notifications if n.id not in state.acked]
    await websocket.send_json(
        {
            "type": "notification_batch",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "notifications": [n.model_dump(mode="json") for n in visible],
        }
    )


async def _notification_loop(websocket: WebSocket, state: ConnectionState, user: User) -> None:
    await _send_batch(websocket, state, user)  # initial batch on connect
    while True:
        await asyncio.sleep(state.interval_seconds)
        await _send_batch(websocket, state, user)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    cookie_value = websocket.cookies.get(SESSION_COOKIE_NAME)
    async with SessionLocal() as db:
        user = await get_current_user_from_cookie_value(db, cookie_value)

    if user is None:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    state = ConnectionState()
    loop_task = asyncio.create_task(_notification_loop(websocket, state, user))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = message.get("type")
            if msg_type == "subscribe":
                state.apply_subscribe(message.get("interval_seconds"), message.get("enabled_types"))
                await websocket.send_json(
                    {
                        "type": "subscribed",
                        "interval_seconds": state.interval_seconds,
                        "enabled_types": sorted(state.enabled_types),
                    }
                )
            elif msg_type == "ack":
                notification_id = message.get("notification_id")
                if notification_id:
                    state.apply_ack(notification_id)
    except WebSocketDisconnect:
        pass
    finally:
        loop_task.cancel()
