import json

from logic import build_row, is_terminal, parse_ts

FAILED_BUILD = {
    "id": "2aa8208d-5e23-46df-bf34-7aa9bb45b05c",
    "status": "FAILURE",
    "createTime": "2026-11-09T17:46:54.123456789Z",
    "startTime": "2026-11-09T17:46:55.000000000Z",
    "finishTime": "2026-11-09T17:49:17.925060Z",
    "buildTriggerId": "trig-1",
    "steps": [
        {"id": "test", "name": "python:3.11", "status": "FAILURE",
         "timing": {"startTime": "2026-11-09T17:47:10.100Z", "endTime": "2026-11-09T17:47:30.600Z"}},
        {"id": "build", "name": "gcr.io/cloud-builders/docker", "status": "QUEUED"},
    ],
    "substitutions": {"COMMIT_SHA": "abc123", "BRANCH_NAME": "main", "_FAULT": "flaky_test"},
    "failureInfo": {"type": "USER_BUILD_STEP", "detail": "step exited with non-zero status: 1"},
    "options": {"machineType": "E2_MEDIUM"},
}


def test_parse_ts_handles_nanoseconds_and_none():
    assert parse_ts("2026-11-09T17:46:54.123456789Z").microsecond == 123456
    assert parse_ts(None) is None


def test_is_terminal():
    assert is_terminal("FAILURE") and is_terminal("SUCCESS")
    assert not is_terminal("WORKING") and not is_terminal("QUEUED")


def test_failed_build_row():
    row = build_row(FAILED_BUILD, log_tail="boom")
    assert row["status"] == "FAILURE"
    assert row["failed_step"] == "test"
    assert row["fault_label"] == "flaky_test"
    assert row["commit_sha"] == "abc123" and row["branch"] == "main"
    assert row["machine_type"] == "E2_MEDIUM"
    assert row["queue_seconds"] == 0.88
    assert abs(row["total_seconds"] - 143.8) < 0.1
    assert abs(row["run_seconds"] - 142.93) < 0.1
    assert "non-zero" in row["failure_info"]
    timings = json.loads(row["step_timings"])
    assert timings[0] == {"id": "test", "status": "FAILURE", "seconds": 20.5}
    assert timings[1]["seconds"] is None
    assert row["log_tail"] == "boom"


def test_minimal_build_does_not_crash():
    row = build_row({"id": "x", "status": "SUCCESS"})
    assert row["build_id"] == "x"
    assert row["failed_step"] is None and row["fault_label"] is None
    assert row["total_seconds"] is None


def test_log_tail_is_truncated():
    row = build_row({"id": "x", "status": "FAILURE"}, log_tail="a" * 50000)
    assert len(row["log_tail"]) == 20000
