"""Pure helper functions (easy to unit test)."""
import re


def validate_title(title, max_length=100):
    """Return (ok, error_message)."""
    if not isinstance(title, str):
        return False, "title must be a string"
    cleaned = title.strip()
    if not cleaned:
        return False, "title must not be empty"
    if len(cleaned) > max_length:
        return False, f"title must be at most {max_length} characters"
    return True, ""


def slugify(text):
    """'Fix Login Bug!' -> 'fix-login-bug'"""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def priority_score(priority, status):
    """Higher means more urgent. Finished tasks always score 0."""
    if status == "done":
        return 0
    weight = {"todo": 1.0, "in_progress": 1.5}.get(status, 1.0)
    return round(priority * weight, 2)


def paginate(items, page=1, per_page=10):
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page must be >= 1")
    start = (page - 1) * per_page
    return items[start:start + per_page]


def summarize(tasks):
    counts = {"todo": 0, "in_progress": 0, "done": 0}
    for task in tasks:
        counts[task["status"]] += 1
    total = len(tasks)
    completion = round(counts["done"] / total * 100, 1) if total else 0.0
    return {"total": total, "by_status": counts, "completion_pct": completion}
