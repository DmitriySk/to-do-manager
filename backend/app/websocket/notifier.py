from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import clock
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.notification import Notification

DUE_SOON_WINDOW_DAYS = 3


async def compute_notifications(
    db: AsyncSession,
    user: User,
    enabled_types: set[str] | None = None,
    today: date | None = None,
) -> list[Notification]:
    """Overdue: status != done and due_date < today.
    Due soon: status != done and due_date within [today, today + 3 days] inclusive."""
    today = today or clock.today()
    enabled_types = enabled_types if enabled_types is not None else {"overdue", "due_soon"}

    result = await db.execute(
        select(Task).where(
            Task.user_id == user.id,
            Task.status != TaskStatus.DONE,
            Task.due_date.is_not(None),
            Task.due_date <= today + timedelta(days=DUE_SOON_WINDOW_DAYS),
        )
    )
    tasks = result.scalars().all()

    notifications: list[Notification] = []
    for task in tasks:
        if task.due_date < today and "overdue" in enabled_types:
            kind = "overdue"
        elif task.due_date >= today and "due_soon" in enabled_types:
            kind = "due_soon"
        else:
            continue

        notifications.append(
            Notification(
                id=f"{kind}:{task.id}",
                task_id=task.id,
                list_id=task.list_id,
                kind=kind,
                title=task.title,
                due_date=task.due_date,
                priority=task.priority.value,
            )
        )

    return notifications
