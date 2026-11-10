re = __import__('re')
from flask import Flask, jsonify, request

def create_app():
    app = Flask(__name__)
    tasks = []

    def generate_slug(title):
        return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

    def compute_score(priority, status):
        # Example formula: priority multiplier with status penalty
        multiplier = 10 if status != 'done' else 0
        return priority * multiplier

    @app.route('/')
    def home():
        return jsonify({
            "status": "online",
            "service": "Agentic CI/CD Pipeline API",
            "message": "Welcome! The service is up and running."
        })

    @app.route('/health')
    def health():
        return jsonify({"status": "ok"})

    @app.route('/tasks', methods=['GET', 'POST'])
    def handle_tasks():
        if request.method == 'POST':
            if not request.is_json:
                return jsonify({"error": "Invalid JSON"}), 400
            data = request.get_json()
            title = data.get("title")
            if not title or not isinstance(title, str) or not title.strip():
                return jsonify({"error": "Title is required"}), 400
            
            title = title.strip()
            if len(title) > 400:
                return jsonify({"error": "Title too long"}), 400

            priority = data.get("priority", 3)
            if priority is True or priority is False or not isinstance(priority, int) or priority not in [1, 2, 3, 4, 5]:
                return jsonify({"error": "Invalid priority"}), 400

            status = data.get("status", "todo")
            if status not in ["todo", "in_progress", "done"]:
                return jsonify({"error": "Invalid status"}), 400

            max_tasks = app.config.get("MAX_TASKS", 100)
            if len(tasks) >= max_tasks:
                return jsonify({"error": "Task limit reached"}), 409

            task_id = len(tasks) + 1
            slug = generate_slug(title)
            score = compute_score(priority, status)
            task = {
                "id": task_id,
                "title": title,
                "slug": slug,
                "priority": priority,
                "status": status,
                "score": score
            }
            tasks.append(task)
            return jsonify(task), 201

        # GET /tasks with filters, sorting, pagination
        status_filter = request.args.get("status")
        if status_filter and status_filter not in ["todo", "in_progress", "done"]:
            return jsonify({"error": "Invalid status filter"}), 400

        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid pagination parameters"}), 400

        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({"error": "Invalid pagination"}), 400

        filtered = [t for t in tasks if not status_filter or t["status"] == status_filter]
        
        sort_by = request.args.get("sort")
        if sort_by == "score":
            filtered = sorted(filtered, key=lambda x: x["score"], reverse=True)

        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = filtered[start:end]

        return jsonify({
            "items": paginated_items,
            "total": len(filtered),
            "page": page,
            "per_page": per_page
        })

    @app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_single_task(task_id):
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return jsonify({"error": "Not found"}), 404

        if request.method == 'GET':
            return jsonify(task)

        if request.method == 'DELETE':
            tasks.remove(task)
            return '', 204

        if request.method == 'PUT':
            if not request.is_json:
                return jsonify({"error": "Invalid JSON"}), 400
            data = request.get_json()
            
            if "title" in data:
                title = data.get("title")
                if not title or not isinstance(title, str) or not title.strip():
                    return jsonify({"error": "Invalid title"}), 400
                task["title"] = title.strip()
                task["slug"] = generate_slug(task["title"])

            if "priority" in data:
                priority = data.get("priority")
                if priority is True or priority is False or not isinstance(priority, int) or priority not in [1, 2, 3, 4, 5]:
                    return jsonify({"error": "Invalid priority"}), 400
                task["priority"] = priority

            if "status" in data:
                status = data.get("status")
                if status not in ["todo", "in_progress", "done"]:
                    return jsonify({"error": "Invalid status"}), 400
                task["status"] = status

            task["score"] = compute_score(task["priority"], task["status"])
            return jsonify(task)

    @app.route('/stats', methods=['GET'])
    def get_stats():
        total = len(tasks)
        done_count = len([t for t in tasks if t["status"] == "done"])
        completion_pct = (done_count / total * 100.0) if total > 0 else 0.0
        return jsonify({
            "total": total,
            "todo": len([t for t in tasks if t["status"] == "todo"]),
            "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
            "done": done_count,
            "completion_pct": completion_pct
        })

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
