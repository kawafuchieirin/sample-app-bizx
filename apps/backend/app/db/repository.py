"""Single-table repository for boards and tasks.

Returns plain dicts (later validated by the API schemas). Raises NotFoundError
when a resource does not exist or does not belong to the requesting user.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from boto3.dynamodb.conditions import ConditionBase, Key
from ulid import ULID

from app.db.table import GSI1_NAME, get_table
from app.models import Priority, Status

# due_date sentinel so tasks without a due date sort last within a status.
_DUE_SENTINEL = "9999-12-31"


class NotFoundError(Exception):
    """Raised when a board or task cannot be found for the given user."""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _new_id() -> str:
    return str(ULID())


# --- key builders --------------------------------------------------------


def _user_pk(user_id: str) -> str:
    return f"USER#{user_id}"


def _board_sk(board_id: str) -> str:
    return f"BOARD#{board_id}"


def _task_sk(task_id: str) -> str:
    return f"TASK#{task_id}"


def _board_gsi1pk(board_id: str) -> str:
    return f"BOARD#{board_id}"


def _task_gsi1sk(status: str, due_date: str | None, task_id: str) -> str:
    due = due_date or _DUE_SENTINEL
    return f"STATUS#{status}#DUE#{due}#{task_id}"


# --- serialization -------------------------------------------------------


def _to_board(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "name": item["name"],
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
    }


def _to_task(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "board_id": item["board_id"],
        "title": item["title"],
        "description": item.get("description", ""),
        "status": item["status"],
        "priority": item["priority"],
        "due_date": item.get("due_date"),
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
    }


# --- boards --------------------------------------------------------------


def create_board(user_id: str, name: str) -> dict[str, Any]:
    now = _now_iso()
    board_id = _new_id()
    item = {
        "PK": _user_pk(user_id),
        "SK": _board_sk(board_id),
        "type": "board",
        "id": board_id,
        "user_id": user_id,
        "name": name,
        "created_at": now,
        "updated_at": now,
    }
    get_table().put_item(Item=item)
    return _to_board(item)


def list_boards(user_id: str) -> list[dict[str, Any]]:
    resp = get_table().query(
        KeyConditionExpression=Key("PK").eq(_user_pk(user_id)) & Key("SK").begins_with("BOARD#")
    )
    return [_to_board(i) for i in resp.get("Items", [])]


def get_board(user_id: str, board_id: str) -> dict[str, Any]:
    resp = get_table().get_item(Key={"PK": _user_pk(user_id), "SK": _board_sk(board_id)})
    item = resp.get("Item")
    if item is None:
        raise NotFoundError(f"board {board_id} not found")
    return _to_board(item)


def update_board(user_id: str, board_id: str, name: str) -> dict[str, Any]:
    # Ensure it exists (and belongs to the user) before updating.
    get_board(user_id, board_id)
    resp = get_table().update_item(
        Key={"PK": _user_pk(user_id), "SK": _board_sk(board_id)},
        UpdateExpression="SET #n = :name, updated_at = :now",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={":name": name, ":now": _now_iso()},
        ReturnValues="ALL_NEW",
    )
    return _to_board(resp["Attributes"])


def delete_board(user_id: str, board_id: str) -> None:
    get_board(user_id, board_id)  # raises NotFoundError if missing
    table = get_table()
    # Delete all tasks belonging to this board, then the board itself.
    task_items = _query_board_tasks(board_id)
    with table.batch_writer() as batch:
        for t in task_items:
            batch.delete_item(Key={"PK": t["PK"], "SK": t["SK"]})
        batch.delete_item(Key={"PK": _user_pk(user_id), "SK": _board_sk(board_id)})


# --- tasks ---------------------------------------------------------------


def _query_board_tasks(board_id: str, status: Status | None = None) -> list[dict[str, Any]]:
    key_expr: ConditionBase = Key("GSI1PK").eq(_board_gsi1pk(board_id))
    if status is not None:
        key_expr = key_expr & Key("GSI1SK").begins_with(f"STATUS#{status.value}#")
    resp = get_table().query(IndexName=GSI1_NAME, KeyConditionExpression=key_expr)
    return list(resp.get("Items", []))


def create_task(
    user_id: str,
    board_id: str,
    *,
    title: str,
    description: str,
    status: Status,
    priority: Priority,
    due_date: date | None,
) -> dict[str, Any]:
    now = _now_iso()
    task_id = _new_id()
    due_str = due_date.isoformat() if due_date else None
    item = {
        "PK": _user_pk(user_id),
        "SK": _task_sk(task_id),
        "GSI1PK": _board_gsi1pk(board_id),
        "GSI1SK": _task_gsi1sk(status.value, due_str, task_id),
        "type": "task",
        "id": task_id,
        "board_id": board_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "status": status.value,
        "priority": priority.value,
        "due_date": due_str,
        "created_at": now,
        "updated_at": now,
    }
    get_table().put_item(Item=item)
    return _to_task(item)


def list_tasks(
    board_id: str,
    *,
    status: Status | None = None,
    sort: str | None = None,
) -> list[dict[str, Any]]:
    items = _query_board_tasks(board_id, status)
    tasks = [_to_task(i) for i in items]
    if sort == "priority":
        order = {Priority.HIGH.value: 0, Priority.MEDIUM.value: 1, Priority.LOW.value: 2}
        tasks.sort(key=lambda t: order.get(t["priority"], 99))
    # Default (sort is None or "due"): GSI1SK already orders by status then due.
    return tasks


def get_task(user_id: str, task_id: str) -> dict[str, Any]:
    resp = get_table().get_item(Key={"PK": _user_pk(user_id), "SK": _task_sk(task_id)})
    item = resp.get("Item")
    if item is None:
        raise NotFoundError(f"task {task_id} not found")
    return _to_task(item)


def update_task(
    user_id: str,
    task_id: str,
    *,
    fields: dict[str, Any],
    clear_due_date: bool = False,
) -> dict[str, Any]:
    """Apply a partial update. `fields` may contain title, description,
    status, priority, due_date (a date). `clear_due_date` removes the due date.
    """
    # Read current item to recompute GSI1SK when status/due changes.
    resp = get_table().get_item(Key={"PK": _user_pk(user_id), "SK": _task_sk(task_id)})
    current = resp.get("Item")
    if current is None:
        raise NotFoundError(f"task {task_id} not found")

    raw_status = fields.get("status") or current["status"]
    new_status = raw_status.value if isinstance(raw_status, Status) else str(raw_status)

    new_due: str | None
    if clear_due_date:
        new_due = None
    elif "due_date" in fields and fields["due_date"] is not None:
        due_val = fields["due_date"]
        new_due = due_val.isoformat() if isinstance(due_val, date) else str(due_val)
    else:
        due_current = current.get("due_date")
        new_due = str(due_current) if due_current is not None else None

    updates: dict[str, Any] = {
        "title": fields.get("title", current["title"]),
        "description": fields.get("description", current.get("description", "")),
        "status": new_status,
        "priority": _as_value(fields.get("priority", current["priority"])),
        "due_date": new_due,
        "updated_at": _now_iso(),
        "GSI1SK": _task_gsi1sk(new_status, new_due, task_id),
    }

    set_expr = ", ".join(f"#{k} = :{k}" for k in updates)
    names = {f"#{k}": k for k in updates}
    values = {f":{k}": v for k, v in updates.items()}
    result = get_table().update_item(
        Key={"PK": _user_pk(user_id), "SK": _task_sk(task_id)},
        UpdateExpression=f"SET {set_expr}",
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
        ReturnValues="ALL_NEW",
    )
    return _to_task(result["Attributes"])


def delete_task(user_id: str, task_id: str) -> None:
    resp = get_table().delete_item(
        Key={"PK": _user_pk(user_id), "SK": _task_sk(task_id)},
        ReturnValues="ALL_OLD",
    )
    if "Attributes" not in resp:
        raise NotFoundError(f"task {task_id} not found")


def _as_value(v: Any) -> Any:
    """Return the .value of a StrEnum, else the value unchanged."""
    return v.value if isinstance(v, (Status, Priority)) else v
