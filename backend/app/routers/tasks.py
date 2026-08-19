from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import clock
from app.database import get_db
from app.dependencies import get_current_user
from app.models.list_project import ListProject
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


async def _get_owned_task(db: AsyncSession, task_id: int, user: User) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("", response_model=list[TaskOut])
async def get_tasks(
    list_id: int | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    due_category: str | None = Query(default=None, pattern="^(overdue|today|next_7_days|all)$"),
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Task).where(Task.user_id == user.id)

    if list_id is not None:
        stmt = stmt.where(Task.list_id == list_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))

    if due_category and due_category != "all":
        today = clock.today()
        if due_category == "overdue":
            stmt = stmt.where(Task.due_date.is_not(None), Task.due_date < today)
        elif due_category == "today":
            stmt = stmt.where(Task.due_date == today)
        elif due_category == "next_7_days":
            stmt = stmt.where(Task.due_date.is_not(None), Task.due_date >= today, Task.due_date <= today + timedelta(days=7))

    stmt = stmt.order_by(Task.due_date.is_(None), Task.due_date, Task.created_at)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    list_result = await db.execute(
        select(ListProject).where(ListProject.id == payload.list_id, ListProject.user_id == user.id)
    )
    if list_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="List not found")

    task = Task(
        list_id=payload.list_id,
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        due_date=payload.due_date,
        priority=payload.priority,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await _get_owned_task(db, task_id, user)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await _get_owned_task(db, task_id, user)

    data = payload.model_dump(exclude_unset=True, exclude={"clear_due_date"})
    for field, value in data.items():
        if field == "due_date" and value is None:
            continue  # handled below via explicit clear_due_date flag
        setattr(task, field, value)

    if payload.clear_due_date:
        task.due_date = None
    elif payload.due_date is not None:
        task.due_date = payload.due_date

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    task = await _get_owned_task(db, task_id, user)
    await db.delete(task)
    await db.commit()
