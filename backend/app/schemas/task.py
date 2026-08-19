from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    list_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    due_date: date | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    priority: TaskPriority | None = None
    # Explicit flag to allow clearing due_date to null via PATCH.
    clear_due_date: bool = False


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    list_id: int
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
