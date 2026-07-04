"""Task endpoints.

Tasks nested under a board (`/boards/{board_id}/tasks`) for listing/creation,
and addressed directly by id (`/tasks/{task_id}`) for read/update/delete.
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.api.schemas import TaskCreate, TaskOut, TaskUpdate
from app.db import repository
from app.db.repository import NotFoundError
from app.deps import CurrentUser
from app.models import Status

board_tasks_router = APIRouter(prefix="/boards/{board_id}/tasks", tags=["tasks"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


def _ensure_board(user_id: str, board_id: str) -> None:
    try:
        repository.get_board(user_id, board_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@board_tasks_router.get("", response_model=list[TaskOut])
def list_tasks(
    board_id: str,
    user_id: CurrentUser,
    task_status: Annotated[Status | None, Query(alias="status")] = None,
    sort: Annotated[Literal["due", "priority"] | None, Query()] = None,
) -> list[TaskOut]:
    _ensure_board(user_id, board_id)
    tasks = repository.list_tasks(board_id, status=task_status, sort=sort)
    return [TaskOut.model_validate(t) for t in tasks]


@board_tasks_router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(board_id: str, payload: TaskCreate, user_id: CurrentUser) -> TaskOut:
    _ensure_board(user_id, board_id)
    task = repository.create_task(
        user_id,
        board_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    return TaskOut.model_validate(task)


@tasks_router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str, user_id: CurrentUser) -> TaskOut:
    try:
        task = repository.get_task(user_id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskOut.model_validate(task)


@tasks_router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, user_id: CurrentUser) -> TaskOut:
    fields = payload.model_dump(exclude_unset=True, exclude={"clear_due_date"})
    try:
        task = repository.update_task(
            user_id, task_id, fields=fields, clear_due_date=payload.clear_due_date
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskOut.model_validate(task)


@tasks_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, user_id: CurrentUser) -> None:
    try:
        repository.delete_task(user_id, task_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
