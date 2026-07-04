"""Domain enums shared across the API and persistence layers."""

from __future__ import annotations

from enum import StrEnum


class Status(StrEnum):
    """Kanban column a task currently sits in."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
