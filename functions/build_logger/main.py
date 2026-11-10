"""Cloud Run function: logs EVERY finished build (success AND failure) to BigQuery.

Trigger: Pub/Sub topic `cloud-builds` (Cloud Build publishes there on every status change).
"""
import base64
import json
import os
import time

import functions_framework

from logic import build_row, is_terminal

BQ_TABLE = os.environ.get("BQ_TABLE", "cicd_metrics.build_runs")  # dataset.table
LOG_LINES = int(os.environ.get("LOG_LINES", "100"))


def fetch_log_tail(build_id, create_time=None, retries=3, wait=8):
    """Last LOG_LINES lines of the build log from Cloud Logging (may lag a few seconds)."""
    from google.cloud import logging as cloud_logging

    client = cloud_logging.Client()
    flt = f'resource.type="build" AND resource.labels.build_id="{build_id}"'
    if create_time:
        flt += f' AND timestamp>="{create_time}"'
    entries = []
    for attempt in range(retries):
        entries = list(client.list_entries(
            filter_=flt, order_by=cloud_logging.DESCENDING, max_results=LOG_LINES))
        if entries:
            break
        time.sleep(wait)
    lines = []
    for entry in reversed(entries):  # oldest -> newest
        payload = entry.payload
        lines.append(payload.rstrip() if isinstance(payload, str) else json.dumps(payload))
    return "\n".join(lines)


@functions_framework.cloud_event
def handle_build_event(cloud_event):
    message = cloud_event.data["message"]
    build = json.loads(base64.b64decode(message["data"]).decode("utf-8"))

    if not is_terminal(build.get("status")):
        return  # ignore QUEUED / WORKING notifications

    try:
        log_tail = fetch_log_tail(build["id"], build.get("createTime"))
    except Exception as exc:  # never lose the row just because logs failed
        print(f"log fetch failed: {exc}")
        log_tail = ""

    row = build_row(build, log_tail)

    from google.cloud import bigquery

    client = bigquery.Client()
    table_id = f"{client.project}.{BQ_TABLE}"
    errors = client.insert_rows_json(table_id, [row], row_ids=[row["build_id"]])
    if errors:
        raise RuntimeError(f"BigQuery insert failed: {errors}")
    print(f'logged build {row["build_id"]} status={row["status"]}')
