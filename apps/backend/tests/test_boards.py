"""Board endpoint behaviour, including per-user isolation."""

from __future__ import annotations


def test_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_requires_auth(client):
    assert client.get("/api/v1/boards").status_code == 401  # no bearer token


def test_create_and_list_board(client, auth_headers):
    headers = auth_headers("user-1")
    created = client.post("/api/v1/boards", json={"name": "Work"}, headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Work"
    assert body["id"]

    listed = client.get("/api/v1/boards", headers=headers)
    assert listed.status_code == 200
    assert [b["id"] for b in listed.json()] == [body["id"]]


def test_boards_are_isolated_per_user(client, auth_headers):
    client.post("/api/v1/boards", json={"name": "Alice board"}, headers=auth_headers("alice"))
    bob = client.get("/api/v1/boards", headers=auth_headers("bob"))
    assert bob.json() == []


def test_update_board(client, auth_headers):
    headers = auth_headers()
    board_id = client.post("/api/v1/boards", json={"name": "old"}, headers=headers).json()["id"]
    resp = client.patch(f"/api/v1/boards/{board_id}", json={"name": "new"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "new"


def test_update_other_users_board_is_404(client, auth_headers):
    board_id = client.post(
        "/api/v1/boards", json={"name": "alice"}, headers=auth_headers("alice")
    ).json()["id"]
    resp = client.patch(
        f"/api/v1/boards/{board_id}", json={"name": "hijack"}, headers=auth_headers("bob")
    )
    assert resp.status_code == 404


def test_delete_board_removes_its_tasks(client, auth_headers):
    headers = auth_headers()
    board_id = client.post("/api/v1/boards", json={"name": "b"}, headers=headers).json()["id"]
    task_id = client.post(
        f"/api/v1/boards/{board_id}/tasks", json={"title": "t"}, headers=headers
    ).json()["id"]

    assert client.delete(f"/api/v1/boards/{board_id}", headers=headers).status_code == 204
    assert client.get(f"/api/v1/tasks/{task_id}", headers=headers).status_code == 404


def test_board_name_validation(client, auth_headers):
    resp = client.post("/api/v1/boards", json={"name": ""}, headers=auth_headers())
    assert resp.status_code == 422
