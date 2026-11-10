import pytest
from app.evaluator import evaluate_pipelines

def test_pipeline_evaluation():
    report = evaluate_pipelines()
    assert "baseline" in report
    assert "agentic" in report
    assert report["agentic"]["avg_mttr_minutes"] < report["baseline"]["avg_mttr_minutes"]
    assert report["mttr_improvement_multiplier"] > 1.0
