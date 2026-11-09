import pytest

from app.store import TaskStore
from app.utils import paginate, priority_score, slugify, summarize, validate_title


# ---- validate_title -------------------------------------------------------
def test_validate_title_accepts_normal_text():
    assert validate_title("Buy milk") == (True, "")


def test_validate_title_rejects_empty_and_whitespace():
    assert validate_title("")[0] is False
    assert validate_title("    ")[0] is False


def test_validate_title_rejects_non_string():
    ok, message = validate_title(123)
    assert ok is False
    assert "string" in message


def test_validate_title_rejects_too_long():
    ok, message = validate_title("x" * 101, max_length=100)
    assert ok is False
    assert "100" in message


def test_validate_title_accepts_exact_max_length():
    assert validate_title("x" * 100, max_length=100)[0] is True


# ---- slugify ---------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected",
    [
        ("Fix Login Bug!", "fix-login-bug"),
        ("  spaced   out  ", "spaced-out"),
        ("Already-slugged", "already-slugged"),
        ("C++ & Python", "c-python"),
        ("!!!", ""),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected


# ---- priority_score ----------------------------------------------------------
def test_priority_score_todo():
    assert priority_score(4, "todo") == 4.0


def test_priority_score_in_progress_is_boosted():
    assert priority_score(4, "in_progress") == 6.0


def test_priority_score_done_is_zero():
    assert priority_score(5, "done") == 0


# ---- paginate ------------------------------------------------------------------
def test_paginate_first_page():
    assert paginate(list(range(25)), page=1, per_page=10) == list(range(10))


def test_paginate_last_partial_page():
    assert paginate(list(range(25)), page=3, per_page=10) == [20, 21, 22, 23, 24]


def test_paginate_page_beyond_end_is_empty():
    assert paginate(list(range(5)), page=9, per_page=10) == []


@pytest.mark.parametrize("page, per_page", [(0, 10), (1, 0), (-1, 5)])
def test_paginate_rejects_bad_values(page, per_page):
    with pytest.raises(ValueError):
        paginate([1, 2, 3], page, per_page)


# ---- summarize -----------------------------------------------------------------
def test_summarize_empty():
    assert summarize([]) == {
        "total": 0,
        "by_status": {"todo": 0, "in_progress": 0, "done": 0},
        "completion_pct": 0.0,
    }


def test_summarize_counts_and_percentage():
    tasks = [{"status": "done"}, {"status": "done"}, {"status": "todo"}, {"status": "in_progress"}]
    result = summarize(tasks)
    assert result["total"] == 4
    assert result["by_status"] == {"todo": 1, "in_progress": 1, "done": 2}
    assert result["completion_pct"] == 50.0


# ---- TaskStore ---------------------------------------------------------------------
def test_store_assigns_incrementing_ids():
    store = TaskStore()
    assert store.add({"title": "a"})["id"] == 1
    assert store.add({"title": "b"})["id"] == 2


def test_store_delete_and_clear():
    store = TaskStore()
    store.add({"title": "a"})
    assert store.delete(1) is True
    assert store.delete(1) is False
    store.add({"title": "b"})
    store.clear()
    assert len(store) == 0
