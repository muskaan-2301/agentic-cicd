# ---- health ------------------------------------------------------------------
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


# ---- create -------------------------------------------------------------------
def test_create_task_defaults(client):
    response = client.post("/tasks", json={"title": "Write report"})
    body = response.get_json()
    assert response.status_code == 201
    assert body["id"] == 1
    assert body["slug"] == "write-report"
    assert body["priority"] == 3
    assert body["status"] == "todo"


def test_create_task_strips_title(client):
    response = client.post("/tasks", json={"title": "  padded  "})
    assert response.get_json()["title"] == "padded"


def test_create_task_requires_json_body(client):
    assert client.post("/tasks", data="not json").status_code == 400


def test_create_task_missing_title(client):
    assert client.post("/tasks", json={"priority": 2}).status_code == 400


def test_create_task_title_too_long(client):
    assert client.post("/tasks", json={"title": "x" * 500}).status_code == 400


def test_create_task_invalid_priority(client):
    assert client.post("/tasks", json={"title": "a", "priority": 9}).status_code == 400
    assert client.post("/tasks", json={"title": "a", "priority": "high"}).status_code == 400
    assert client.post("/tasks", json={"title": "a", "priority": True}).status_code == 400


def test_create_task_invalid_status(client):
    assert client.post("/tasks", json={"title": "a", "status": "blocked"}).status_code == 400


def test_task_limit_returns_conflict(app, client):
    app.config["MAX_TASKS"] = 2
    client.post("/tasks", json={"title": "one"})
    client.post("/tasks", json={"title": "two"})
    assert client.post("/tasks", json={"title": "three"}).status_code == 409


# ---- read ---------------------------------------------------------------------
def test_get_task(client, make_task):
    created = make_task("Read me")
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Read me"


def test_get_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_list_tasks_empty(client):
    body = client.get("/tasks").get_json()
    assert body["items"] == []
    assert body["total"] == 0


def test_list_tasks_filter_by_status(client, make_task):
    make_task("a", status="todo")
    make_task("b", status="done")
    body = client.get("/tasks?status=done").get_json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "b"


def test_list_tasks_invalid_status_filter(client):
    assert client.get("/tasks?status=nope").status_code == 400


def test_list_tasks_sorted_by_score(client, make_task):
    make_task("low", priority=1)
    make_task("high", priority=5)
    items = client.get("/tasks?sort=score").get_json()["items"]
    assert [t["title"] for t in items] == ["high", "low"]


def test_list_tasks_pagination(client, make_task):
    for i in range(12):
        make_task(f"task {i}")
    body = client.get("/tasks?page=2&per_page=5").get_json()
    assert len(body["items"]) == 5
    assert body["total"] == 12
    assert body["page"] == 2


def test_list_tasks_rejects_bad_pagination(client):
    assert client.get("/tasks?page=0").status_code == 400
    assert client.get("/tasks?per_page=9999").status_code == 400
    assert client.get("/tasks?page=abc").status_code == 400


# ---- update -------------------------------------------------------------------
def test_update_task_status_recomputes_score(client, make_task):
    created = make_task("finish me", priority=4)
    response = client.put(f"/tasks/{created['id']}", json={"status": "done"})
    assert response.status_code == 200
    assert response.get_json()["score"] == 0


def test_update_task_title_changes_slug(client, make_task):
    created = make_task("old name")
    body = client.put(f"/tasks/{created['id']}", json={"title": "New Name"}).get_json()
    assert body["slug"] == "new-name"


def test_update_task_validation_errors(client, make_task):
    created = make_task("valid")
    url = f"/tasks/{created['id']}"
    assert client.put(url, json={"title": ""}).status_code == 400
    assert client.put(url, json={"priority": 0}).status_code == 400
    assert client.put(url, json={"status": "bogus"}).status_code == 400


def test_update_missing_task_returns_404(client):
    assert client.put("/tasks/42", json={"status": "done"}).status_code == 404


# ---- delete -------------------------------------------------------------------
def test_delete_task(client, make_task):
    created = make_task("temporary")
    assert client.delete(f"/tasks/{created['id']}").status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_missing_task_returns_404(client):
    assert client.delete("/tasks/42").status_code == 404


# ---- stats --------------------------------------------------------------------
def test_stats_reflect_current_tasks(client, make_task):
    make_task("a", status="done")
    make_task("b", status="todo")
    body = client.get("/stats").get_json()
    assert body["total"] == 2
    assert body["completion_pct"] == 50.0
