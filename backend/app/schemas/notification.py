from datetime import date

from pydantic import BaseModel


class Notification(BaseModel):
    id: str
    task_id: int
    list_id: int
    kind: str  # "overdue" | "due_soon"
    title: str
    due_date: date
    priority: str
