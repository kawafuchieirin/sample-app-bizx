"""Task endpoint behaviour: CRUD, status moves, filtering and sorting."""

from __future__ import annotations

import pytest


@pytest.fixture
def board(client, auth_headers):
    headers = auth_headers()
    board_id = client.post("/api/v1/boards", json={"name": "b"}, headers=headers).json()["id"]
    return board_id, headers


def test_create_task_defaults(client, board):
    board_id, headers = board
    resp = client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "buy milk"}, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "buy milk"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["due_date"] is None
    assert body["board_id"] == board_id


def test_create_task_with_fields(client, board):
    board_id, headers = board
    payload = {
        "title": "ship release",
        "description": "cut v1",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-07-10",
    }
    body = client.post(f"/api/v1/boards/{board_id}/tasks", json=payload, headers=headers).json()
    assert body["status"] == "in_progress"
    assert body["priority"] == "high"
    assert body["due_date"] == "2026-07-10"


def test_create_task_on_missing_board_is_404(client, auth_headers):
    resp = client.post("/api/v1/boards/nope/tasks", json={"title": "x"}, headers=auth_headers())
    assert resp.status_code == 404


def test_get_and_update_task_moves_status(client, board):
    board_id, headers = board
    task_id = client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "t"}, headers=headers
    ).json()["id"]

    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"

    got = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert got.json()["status"] == "done"


def test_update_clears_due_date(client, board):
    board_id, headers = board
    task_id = client.post(
        f"/api/v1/boards/{board_id}/tasks",
        json={"title": "t", "due_date": "2026-08-01"},
        headers=headers,
    ).json()["id"]

    resp = client.patch(f"/api/v1/tasks/{task_id}", json={"clear_due_date": True}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["due_date"] is None


def test_delete_task(client, board):
    board_id, headers = board
    task_id = client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "t"}, headers=headers
    ).json()["id"]
    assert client.delete(f"/api/v1/tasks/{task_id}", headers=headers).status_code == 204
    assert client.get(f"/api/v1/tasks/{task_id}", headers=headers).status_code == 404


def test_tasks_isolated_per_user(client, board, auth_headers):
    board_id, headers = board
    task_id = client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "secret"}, headers=headers
    ).json()["id"]
    # Another user cannot read the task by id.
    assert (
        client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers("intruder")).status_code == 404
    )


def test_list_filter_by_status(client, board):
    board_id, headers = board
    client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "a", "status": "todo"}, headers=headers
    )
    client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "b", "status": "done"}, headers=headers
    )
    resp = client.get(f"/api/v1/boards/{board_id}/tasks?status=done", headers=headers)
    titles = [t["title"] for t in resp.json()]
    assert titles == ["b"]


def test_list_sorted_by_priority(client, board):
    board_id, headers = board
    for title, prio in [("low", "low"), ("high", "high"), ("mid", "medium")]:
        client.post(
            f"/api/v1/boards/{board_id}/tasks",
            json={"title": title, "priority": prio},
            headers=headers,
        )
    resp = client.get(f"/api/v1/boards/{board_id}/tasks?sort=priority", headers=headers)
    assert [t["title"] for t in resp.json()] == ["high", "mid", "low"]


def test_list_sorted_by_due_date(client, board):
    board_id, headers = board
    client.post(
        f"/api/v1/boards/{board_id}/tasks",
        json={"title": "later", "due_date": "2026-12-31"},
        headers=headers,
    )
    client.post(
        f"/api/v1/boards/{board_id}/tasks",
        json={"title": "sooner", "due_date": "2026-07-05"},
        headers=headers,
    )
    resp = client.get(f"/api/v1/boards/{board_id}/tasks?sort=due", headers=headers)
    assert [t["title"] for t in resp.json()] == ["sooner", "later"]
