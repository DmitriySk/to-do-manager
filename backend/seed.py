"""Standalone CLI alternative to POST /api/dev/seed.

Usage:
    python seed.py <provider> <provider_user_id>

Creates (or reuses) a user identified by (provider, provider_user_id) and
seeds sample lists/tasks for them, without needing a running server.
Example:
    python seed.py google local-dev-user
"""
import asyncio
import sys
from datetime import timedelta

from sqlalchemy import select

from app import clock
from app.database import SessionLocal
from app.models.list_project import ListProject
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User


async def main(provider: str, provider_user_id: str) -> None:
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.provider == provider, User.provider_user_id == provider_user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                provider=provider,
                provider_user_id=provider_user_id,
                display_name=f"{provider.title()} Dev User",
                email=None,
            )
            db.add(user)
            await db.flush()

        today = clock.today()
        work = ListProject(name="Work", user_id=user.id)
        personal = ListProject(name="Personal", user_id=user.id)
        db.add_all([work, personal])
        await db.flush()

        db.add_all(
            [
                Task(list_id=work.id, user_id=user.id, title="Finish quarterly report",
                     status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH, due_date=today - timedelta(days=2)),
                Task(list_id=work.id, user_id=user.id, title="Reply to client email",
                     status=TaskStatus.TODO, priority=TaskPriority.MEDIUM, due_date=today),
                Task(list_id=work.id, user_id=user.id, title="Prepare sprint demo",
                     status=TaskStatus.TODO, priority=TaskPriority.HIGH, due_date=today + timedelta(days=2)),
                Task(list_id=personal.id, user_id=user.id, title="Renew gym membership",
                     status=TaskStatus.TODO, priority=TaskPriority.LOW, due_date=today + timedelta(days=6)),
                Task(list_id=personal.id, user_id=user.id, title="Pay electricity bill",
                     status=TaskStatus.TODO, priority=TaskPriority.HIGH, due_date=today - timedelta(days=5)),
            ]
        )
        await db.commit()
        print(f"Seeded sample data for user id={user.id} ({provider}:{provider_user_id})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
