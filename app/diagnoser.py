import os
from google import genai
from google.genai import types

def diagnose_build_failure(error_logs: str, past_failures_context: str = "") -> str:
    """
    Uses Gemini via Vertex AI / Google GenAI SDK to diagnose CI/CD build failures 
    and suggest remediation steps based on past failures context.
    """
    client = genai.Client()
    
    prompt = f"""
    You are an expert DevOps AI assistant. Analyze the following CI/CD build failure logs 
    and provide a concise root cause diagnosis along with a recommended fix.
    
    Context from Past Failures:
    {past_failures_context}
    
    Current Build Error Logs:
    {error_logs}
    
    Please provide:
    1. Root Cause Analysis
    2. Recommended Remediation Action (e.g., RETRY, SCALE_UP, CODE_FIX)
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    return response.text

if __name__ == "__main__":
    sample_logs = "Step #3 - step timed out or out of memory while building container image."
    print("Sample Diagnosis:", diagnose_build_failure(sample_logs))
