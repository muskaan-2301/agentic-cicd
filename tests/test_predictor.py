import pytest
from app.predictor import predict_build_outcome

def test_predictor_structure():
    result = predict_build_outcome(250.0, 0.1)
    assert "prediction" in result
    assert "risk_score" in result
    assert result["prediction"] in ["PASS", "FAIL"]
    assert 0.0 <= result["risk_score"] <= 1.0
