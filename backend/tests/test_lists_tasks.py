def test_create_list_and_task(auth_client):
    list_resp = auth_client.post("/api/lists", json={"name": "Groceries"})
    assert list_resp.status_code == 201
    list_body = list_resp.json()
    assert list_body["name"] == "Groceries"
    assert list_body["task_count"] == 0

    task_resp = auth_client.post(
        "/api/tasks",
        json={
            "list_id": list_body["id"],
            "title": "Buy milk",
            "description": "2 liters",
            "priority": "high",
            "due_date": "2026-08-20",
        },
    )
    assert task_resp.status_code == 201
    task_body = task_resp.json()
    assert task_body["title"] == "Buy milk"
    assert task_body["status"] == "todo"
    assert task_body["priority"] == "high"

    tasks = auth_client.get("/api/tasks", params={"list_id": list_body["id"]})
    assert tasks.status_code == 200
    assert len(tasks.json()) == 1

    lists = auth_client.get("/api/lists")
    assert lists.status_code == 200
    assert lists.json()[0]["task_count"] == 1


def test_quick_status_change(auth_client):
    list_body = auth_client.post("/api/lists", json={"name": "Work"}).json()
    task_body = auth_client.post(
        "/api/tasks", json={"list_id": list_body["id"], "title": "Ship feature"}
    ).json()

    patch_resp = auth_client.patch(f"/api/tasks/{task_body['id']}", json={"status": "done"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "done"


def test_delete_list_cascades_tasks(auth_client):
    list_body = auth_client.post("/api/lists", json={"name": "Temp"}).json()
    auth_client.post("/api/tasks", json={"list_id": list_body["id"], "title": "Task A"})

    del_resp = auth_client.delete(f"/api/lists/{list_body['id']}")
    assert del_resp.status_code == 204

    tasks = auth_client.get("/api/tasks", params={"list_id": list_body["id"]})
    assert tasks.json() == []


def test_search_and_filter(auth_client):
    list_body = auth_client.post("/api/lists", json={"name": "Misc"}).json()
    auth_client.post("/api/tasks", json={"list_id": list_body["id"], "title": "Write report", "priority": "high"})
    auth_client.post("/api/tasks", json={"list_id": list_body["id"], "title": "Clean desk", "priority": "low"})

    by_search = auth_client.get("/api/tasks", params={"q": "report"})
    assert len(by_search.json()) == 1
    assert by_search.json()[0]["title"] == "Write report"

    by_priority = auth_client.get("/api/tasks", params={"priority": "low"})
    assert len(by_priority.json()) == 1
    assert by_priority.json()[0]["title"] == "Clean desk"
