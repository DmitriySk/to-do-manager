from datetime import date, timedelta

from app.auth.session import SESSION_COOKIE_NAME
from app.database import SessionLocal
from app.dependencies import get_current_user_from_cookie_value
from app.schemas.notification import Notification
from app.websocket.manager import ConnectionState
from app.websocket.notifier import compute_notifications


def test_initial_batch_and_subscribe_ack_over_websocket(auth_client, frozen_clock):
    list_body = auth_client.post("/api/lists", json={"name": "Test"}).json()
    overdue_task = auth_client.post(
        "/api/tasks",
        json={"list_id": list_body["id"], "title": "Overdue task", "due_date": str(frozen_clock - timedelta(days=1))},
    ).json()
    due_soon_task = auth_client.post(
        "/api/tasks",
        json={"list_id": list_body["id"], "title": "Due soon task", "due_date": str(frozen_clock + timedelta(days=2))},
    ).json()
    auth_client.post(
        "/api/tasks",
        json={"list_id": list_body["id"], "title": "Far future task", "due_date": str(frozen_clock + timedelta(days=10))},
    )

    with auth_client.websocket_connect("/ws") as ws:
        initial = ws.receive_json()
        assert initial["type"] == "notification_batch"
        ids = {n["id"] for n in initial["notifications"]}
        assert ids == {f"overdue:{overdue_task['id']}", f"due_soon:{due_soon_task['id']}"}

        # client -> server message that changes server behavior: subscribe
        ws.send_json({"type": "subscribe", "interval_seconds": 45, "enabled_types": ["overdue", "due_soon"]})
        ack = ws.receive_json()
        assert ack["type"] == "subscribed"
        assert ack["interval_seconds"] == 45
        assert set(ack["enabled_types"]) == {"overdue", "due_soon"}


def test_websocket_rejects_unauthenticated_connection(client):
    import pytest
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws"):
            pass


async def test_compute_notifications_respects_status_and_window(auth_client, frozen_clock):
    """Unit-tests the overdue/due-soon rules directly against a frozen clock,
    avoiding a flaky real-time wait for the periodic WS recheck."""
    list_body = auth_client.post("/api/lists", json={"name": "Test"}).json()
    overdue = auth_client.post(
        "/api/tasks",
        json={"list_id": list_body["id"], "title": "Overdue", "due_date": str(frozen_clock - timedelta(days=1))},
    ).json()
    due_soon = auth_client.post(
        "/api/tasks",
        json={"list_id": list_body["id"], "title": "Due soon", "due_date": str(frozen_clock + timedelta(days=3))},
    ).json()
    future = auth_client.post(
        "/api/tasks",
        json={"list_id": list_body["id"], "title": "Future", "due_date": str(frozen_clock + timedelta(days=10))},
    ).json()
    done_overdue = auth_client.post(
        "/api/tasks",
        json={
            "list_id": list_body["id"],
            "title": "Done but overdue",
            "status": "done",
            "due_date": str(frozen_clock - timedelta(days=1)),
        },
    ).json()

    cookie = auth_client.cookies.get(SESSION_COOKIE_NAME)
    async with SessionLocal() as db:
        user = await get_current_user_from_cookie_value(db, cookie)
        notifications = await compute_notifications(db, user, today=frozen_clock)

    ids = {n.id for n in notifications}
    assert f"overdue:{overdue['id']}" in ids
    assert f"due_soon:{due_soon['id']}" in ids
    assert f"overdue:{future['id']}" not in ids
    assert f"due_soon:{future['id']}" not in ids
    assert f"overdue:{done_overdue['id']}" not in ids
    assert len(notifications) == 2


def test_connection_state_ack_excludes_notification():
    state = ConnectionState()
    state.apply_ack("overdue:1")
    notifications = [
        Notification(id="overdue:1", task_id=1, list_id=1, kind="overdue", title="t1", due_date=date(2026, 1, 1), priority="high"),
        Notification(id="due_soon:2", task_id=2, list_id=1, kind="due_soon", title="t2", due_date=date(2026, 1, 2), priority="low"),
    ]
    visible = [n for n in notifications if n.id not in state.acked]
    assert [n.id for n in visible] == ["due_soon:2"]


def test_connection_state_subscribe_clamps_interval():
    state = ConnectionState()
    state.apply_subscribe(interval_seconds=5, enabled_types=["overdue"])
    assert state.interval_seconds == 10  # clamped to configured minimum
    state.apply_subscribe(interval_seconds=10_000, enabled_types=None)
    assert state.interval_seconds == 300  # clamped to configured maximum
    assert state.enabled_types == {"overdue"}
