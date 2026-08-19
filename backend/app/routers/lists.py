from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.list_project import ListProject
from app.models.task import Task
from app.models.user import User
from app.schemas.list_project import ListCreate, ListOut, ListUpdate

router = APIRouter(prefix="/api/lists", tags=["lists"])


async def _get_owned_list(db: AsyncSession, list_id: int, user: User) -> ListProject:
    result = await db.execute(select(ListProject).where(ListProject.id == list_id, ListProject.user_id == user.id))
    list_obj = result.scalar_one_or_none()
    if list_obj is None:
        raise HTTPException(status_code=404, detail="List not found")
    return list_obj


@router.get("", response_model=list[ListOut])
async def get_lists(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(ListProject, func.count(Task.id))
        .outerjoin(Task, Task.list_id == ListProject.id)
        .where(ListProject.user_id == user.id)
        .group_by(ListProject.id)
        .order_by(ListProject.created_at)
    )
    out = []
    for list_obj, task_count in result.all():
        item = ListOut.model_validate(list_obj)
        item.task_count = task_count
        out.append(item)
    return out


@router.post("", response_model=ListOut, status_code=201)
async def create_list(payload: ListCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    list_obj = ListProject(name=payload.name, user_id=user.id)
    db.add(list_obj)
    await db.commit()
    await db.refresh(list_obj)
    return list_obj


@router.patch("/{list_id}", response_model=ListOut)
async def update_list(
    list_id: int,
    payload: ListUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    list_obj = await _get_owned_list(db, list_id, user)
    list_obj.name = payload.name
    await db.commit()
    await db.refresh(list_obj)
    return list_obj


@router.delete("/{list_id}", status_code=204)
async def delete_list(list_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    list_obj = await _get_owned_list(db, list_id, user)
    await db.delete(list_obj)  # cascades to tasks via relationship + FK ON DELETE CASCADE
    await db.commit()
