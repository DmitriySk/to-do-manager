from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import clock
from app.database import get_db
from app.dependencies import get_current_user
from app.models.list_project import ListProject
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

router = APIRouter(prefix="/api/dev", tags=["dev"])


@router.post("/seed")
async def seed_sample_data(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Creates a few sample lists and tasks for the current user, including
    deliberately overdue and due-soon tasks so notifications are visible
    right after seeding. Gated by ENABLE_DEV_ENDPOINTS."""
    today = clock.today()

    work = ListProject(name="Work", user_id=user.id)
    personal = ListProject(name="Personal", user_id=user.id)
    db.add_all([work, personal])
    await db.flush()

    tasks = [
        Task(list_id=work.id, user_id=user.id, title="Finish quarterly report", status=TaskStatus.IN_PROGRESS,
             priority=TaskPriority.HIGH, due_date=today - timedelta(days=2)),
        Task(list_id=work.id, user_id=user.id, title="Reply to client email", status=TaskStatus.TODO,
             priority=TaskPriority.MEDIUM, due_date=today),
        Task(list_id=work.id, user_id=user.id, title="Prepare sprint demo", status=TaskStatus.TODO,
             priority=TaskPriority.HIGH, due_date=today + timedelta(days=2)),
        Task(list_id=work.id, user_id=user.id, title="Review pull requests", status=TaskStatus.DONE,
             priority=TaskPriority.LOW, due_date=today - timedelta(days=1)),
        Task(list_id=personal.id, user_id=user.id, title="Renew gym membership", status=TaskStatus.TODO,
             priority=TaskPriority.LOW, due_date=today + timedelta(days=6)),
        Task(list_id=personal.id, user_id=user.id, title="Book dentist appointment", status=TaskStatus.TODO,
             priority=TaskPriority.MEDIUM, due_date=today + timedelta(days=1)),
        Task(list_id=personal.id, user_id=user.id, title="Plan weekend trip", status=TaskStatus.IN_PROGRESS,
             priority=TaskPriority.LOW, due_date=None),
        Task(list_id=personal.id, user_id=user.id, title="Pay electricity bill", status=TaskStatus.TODO,
             priority=TaskPriority.HIGH, due_date=today - timedelta(days=5)),
    ]
    db.add_all(tasks)
    await db.commit()

    return {"lists_created": 2, "tasks_created": len(tasks)}
