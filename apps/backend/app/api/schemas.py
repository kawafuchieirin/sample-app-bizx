"""Request/response models for the API layer."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Priority, Status

# --- Board ---------------------------------------------------------------


class BoardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class BoardUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    created_at: datetime
    updated_at: datetime


# --- Task ----------------------------------------------------------------


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: Status = Status.TODO
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None


class TaskUpdate(BaseModel):
    """Partial update — only provided fields are changed."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: Status | None = None
    priority: Priority | None = None
    due_date: date | None = None
    # Distinguishes "clear the due date" from "leave it unchanged".
    clear_due_date: bool = False


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    board_id: str
    title: str
    description: str
    status: Status
    priority: Priority
    due_date: date | None
    created_at: datetime
    updated_at: datetime
