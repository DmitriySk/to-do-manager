def test_user_cannot_access_another_users_list_or_tasks(auth_client, second_auth_client):
    list_body = auth_client.post("/api/lists", json={"name": "User A's list"}).json()
    task_body = auth_client.post(
        "/api/tasks", json={"list_id": list_body["id"], "title": "User A's task"}
    ).json()

    # user B cannot read, rename, or delete user A's list
    assert second_auth_client.get("/api/lists").json() == []
    assert second_auth_client.patch(f"/api/lists/{list_body['id']}", json={"name": "hijacked"}).status_code == 404
    assert second_auth_client.delete(f"/api/lists/{list_body['id']}").status_code == 404

    # user B cannot read, edit, or delete user A's task
    assert second_auth_client.get(f"/api/tasks/{task_body['id']}").status_code == 404
    assert second_auth_client.patch(f"/api/tasks/{task_body['id']}", json={"status": "done"}).status_code == 404
    assert second_auth_client.delete(f"/api/tasks/{task_body['id']}").status_code == 404

    # user B creating a task under user A's list is also rejected
    create_resp = second_auth_client.post(
        "/api/tasks", json={"list_id": list_body["id"], "title": "sneaky"}
    )
    assert create_resp.status_code == 404

    # user A's data remains intact
    assert auth_client.get("/api/lists").json()[0]["name"] == "User A's list"
