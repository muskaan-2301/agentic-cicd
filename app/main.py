"""Task-manager REST API. This is the 'application under build' -- the
thing our CI/CD pipeline compiles, tests and (later) predicts failures for."""
from flask import Flask, jsonify, request

from .config import Config
from .store import TaskStore
from .utils import paginate, priority_score, slugify, summarize, validate_title


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    store = TaskStore()
    app.extensions["task_store"] = store

    def error(message, code=400):
        return jsonify(error=message), code

    def valid_priority(value):
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            and value in app.config["VALID_PRIORITIES"]
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error("JSON body required")
        ok, message = validate_title(data.get("title"), app.config["MAX_TITLE_LENGTH"])
        if not ok:
            return error(message)
        priority = data.get("priority", 3)
        if not valid_priority(priority):
            return error("priority must be an integer from 1 to 5")
        status = data.get("status", "todo")
        if status not in app.config["VALID_STATUSES"]:
            return error("invalid status")
        if len(store) >= app.config["MAX_TASKS"]:
            return error("task limit reached", 409)
        title = data["title"].strip()
        task = store.add({
            "title": title,
            "slug": slugify(title),
            "priority": priority,
            "status": status,
            "score": priority_score(priority, status),
        })
        return jsonify(task), 201

    @app.get("/tasks")
    def list_tasks():
        tasks = store.all()
        status = request.args.get("status")
        if status is not None:
            if status not in app.config["VALID_STATUSES"]:
                return error("invalid status")
            tasks = [t for t in tasks if t["status"] == status]
        if request.args.get("sort") == "score":
            tasks = sorted(tasks, key=lambda t: t["score"], reverse=True)
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", app.config["DEFAULT_PAGE_SIZE"]))
        except ValueError:
            return error("page and per_page must be integers")
        if page < 1 or per_page < 1 or per_page > app.config["MAX_PAGE_SIZE"]:
            return error("invalid pagination values")
        return jsonify(
            items=paginate(tasks, page, per_page),
            page=page,
            per_page=per_page,
            total=len(tasks),
        )

    @app.get("/tasks/<int:task_id>")
    def get_task(task_id):
        task = store.get(task_id)
        if task is None:
            return error("task not found", 404)
        return jsonify(task)

    @app.put("/tasks/<int:task_id>")
    def update_task(task_id):
        task = store.get(task_id)
        if task is None:
            return error("task not found", 404)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error("JSON body required")
        fields = {}
        if "title" in data:
            ok, message = validate_title(data["title"], app.config["MAX_TITLE_LENGTH"])
            if not ok:
                return error(message)
            fields["title"] = data["title"].strip()
            fields["slug"] = slugify(fields["title"])
        if "priority" in data:
            if not valid_priority(data["priority"]):
                return error("priority must be an integer from 1 to 5")
            fields["priority"] = data["priority"]
        if "status" in data:
            if data["status"] not in app.config["VALID_STATUSES"]:
                return error("invalid status")
            fields["status"] = data["status"]
        new_priority = fields.get("priority", task["priority"])
        new_status = fields.get("status", task["status"])
        fields["score"] = priority_score(new_priority, new_status)
        return jsonify(store.update(task_id, **fields))

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id):
        if not store.delete(task_id):
            return error("task not found", 404)
        return "", 204

    @app.get("/stats")
    def stats():
        return jsonify(summarize(store.all()))

    return app
