import pytest
from app.remediator import execute_remediation

def test_remediation_retry_within_limit():
    pred = {"prediction": "FAIL", "recommended_action": "RETRY"}
    result = execute_remediation(pred, "Timeout error", current_retry_count=1)
    assert result["action"] == "RETRY"
    assert result["retry_count"] == 2

def test_remediation_guardrail_max_retries():
    pred = {"prediction": "FAIL", "recommended_action": "RETRY"}
    # Exceeds max retries (3)
    result = execute_remediation(pred, "Timeout error", current_retry_count=3)
    assert result["action"] == "NOTIFY_ONLY"
