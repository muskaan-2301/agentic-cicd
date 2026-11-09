import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_task(client):
    """Helper: create a task through the API and return the JSON."""
    def _make(title="Write report", **extra):
        response = client.post("/tasks", json={"title": title, **extra})
        assert response.status_code == 201
        return response.get_json()
    return _make
