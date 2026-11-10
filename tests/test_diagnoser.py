import pytest
from unittest.mock import patch, MagicMock
from app.diagnoser import diagnose_build_failure

@patch('app.diagnoser.genai.Client')
def test_diagnose_build_failure(mock_genai_client):
    mock_response = MagicMock()
    mock_response.text = "Root Cause: OOM Error. Recommendation: SCALE_UP"
    mock_genai_client.return_value.models.generate_content.return_value = mock_response
    
    result = diagnose_build_failure("Out of memory error in build step")
    assert "Root Cause" in result
    assert "Recommendation" in result
