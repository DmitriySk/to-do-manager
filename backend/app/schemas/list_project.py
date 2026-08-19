from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ListUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
