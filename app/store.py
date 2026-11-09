"""A tiny in-memory task store (no database needed for this project)."""


class TaskStore:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def add(self, task):
        task = dict(task)
        task["id"] = self._next_id
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id):
        return self._tasks.get(task_id)

    def update(self, task_id, **fields):
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.update(fields)
        return task

    def delete(self, task_id):
        return self._tasks.pop(task_id, None) is not None

    def all(self):
        return list(self._tasks.values())

    def clear(self):
        self._tasks.clear()
        self._next_id = 1

    def __len__(self):
        return len(self._tasks)
