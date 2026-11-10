import pytest
from app.notifier import send_build_alert

def test_send_build_alert():
    result = send_build_alert("test-build-999", "PASS", "PROCEED")
    assert result["status"] == "SENT"
    assert "test-build-999" in result["message"]
