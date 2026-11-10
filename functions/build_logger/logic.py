"""Pure logic (stdlib only) so it can be unit-tested without any GCP libraries."""
import json
import re
from datetime import datetime, timezone

TERMINAL_STATUSES = {"SUCCESS", "FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED", "EXPIRED"}
FAILED_STEP_STATUSES = {"FAILURE", "TIMEOUT", "INTERNAL_ERROR"}
MAX_LOG_CHARS = 20000


def is_terminal(status):
    return status in TERMINAL_STATUSES


def parse_ts(value):
    """Cloud Build timestamps look like 2026-11-09T17:46:54.123456789Z (nanoseconds)."""
    if not value:
        return None
    value = re.sub(r"(\.\d{6})\d+", r"\1", value)  # nanoseconds -> microseconds
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seconds_between(start, end):
    if start is None or end is None:
        return None
    return round((end - start).total_seconds(), 2)


def build_row(build, log_tail="", now=None):
    """Turn a Cloud Build resource (the Pub/Sub message body) into one BigQuery row."""
    subs = build.get("substitutions") or {}
    create = parse_ts(build.get("createTime"))
    start = parse_ts(build.get("startTime"))
    finish = parse_ts(build.get("finishTime"))

    steps, failed_step = [], None
    for step in build.get("steps") or []:
        timing = step.get("timing") or {}
        name = step.get("id") or step.get("name")
        steps.append({
            "id": name,
            "status": step.get("status"),
            "seconds": seconds_between(parse_ts(timing.get("startTime")),
                                       parse_ts(timing.get("endTime"))),
        })
        if failed_step is None and step.get("status") in FAILED_STEP_STATUSES:
            failed_step = name

    info = build.get("failureInfo") or {}
    failure_info = f'{info.get("type", "")}: {info.get("detail", "")}'.strip(": ") or None

    def iso(ts):
        return ts.isoformat() if ts else None

    return {
        "build_id": build.get("id"),
        "status": build.get("status"),
        "trigger_id": build.get("buildTriggerId"),
        "trigger_name": subs.get("TRIGGER_NAME"),
        "commit_sha": subs.get("COMMIT_SHA"),
        "branch": subs.get("BRANCH_NAME"),
        "machine_type": (build.get("options") or {}).get("machineType"),
        "create_time": iso(create),
        "start_time": iso(start),
        "finish_time": iso(finish),
        "queue_seconds": seconds_between(create, start),
        "run_seconds": seconds_between(start, finish),
        "total_seconds": seconds_between(create, finish),
        "failed_step": failed_step,
        "failure_info": failure_info,
        "step_timings": json.dumps(steps),
        "fault_label": subs.get("_FAULT"),   # ground-truth label set by fault injection
        "log_tail": (log_tail or "")[-MAX_LOG_CHARS:],
        "ingested_at": (now or datetime.now(timezone.utc)).isoformat(),
    }
