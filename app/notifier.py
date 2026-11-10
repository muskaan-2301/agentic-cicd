import os

def send_build_alert(build_id: str, status: str, action_taken: str, details: str = "") -> dict:
    """
    Sends notifications for critical build outcomes and remediation actions 
    (supports simulated alerts, Slack webhooks, or Cloud Monitoring logs).
    """
    message = f"[CI/CD ALERT] Build ID: {build_id} | Status: {status} | Action: {action_taken} | Details: {details}"
    
    # In production, this would dispatch to a webhook (e.g., Slack/Teams) or email.
    print(message)
    
    return {
        "status": "SENT",
        "message": message
    }

if __name__ == "__main__":
    send_build_alert("build-12345", "FAIL", "RETRY", "Timeout in test stage")
