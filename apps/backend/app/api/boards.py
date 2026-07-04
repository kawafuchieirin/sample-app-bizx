"""Board endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.schemas import BoardCreate, BoardOut, BoardUpdate
from app.db import repository
from app.db.repository import NotFoundError
from app.deps import CurrentUser

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=list[BoardOut])
def list_boards(user_id: CurrentUser) -> list[BoardOut]:
    return [BoardOut.model_validate(b) for b in repository.list_boards(user_id)]


@router.post("", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
def create_board(payload: BoardCreate, user_id: CurrentUser) -> BoardOut:
    board = repository.create_board(user_id, payload.name)
    return BoardOut.model_validate(board)


@router.patch("/{board_id}", response_model=BoardOut)
def update_board(board_id: str, payload: BoardUpdate, user_id: CurrentUser) -> BoardOut:
    try:
        board = repository.update_board(user_id, board_id, payload.name)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BoardOut.model_validate(board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board(board_id: str, user_id: CurrentUser) -> None:
    try:
        repository.delete_board(user_id, board_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
