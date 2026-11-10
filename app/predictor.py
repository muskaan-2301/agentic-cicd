import random

def predict_build_outcome(build_duration_seconds: float, historical_failure_rate: float = 0.1) -> dict:
    """
    Predicts whether a build is likely to succeed or fail based on duration 
    and historical metrics.
    """
    risk_score = 0.0
    
    if build_duration_seconds > 600:
        risk_score += 0.5
    
    if historical_failure_rate > 0.2:
        risk_score += 0.3
        
    risk_score += random.uniform(0.0, 0.2)
    
    prediction = "FAIL" if risk_score > 0.6 else "PASS"
    
    return {
        "prediction": prediction,
        "risk_score": round(risk_score, 2),
        "recommended_action": "RETRY" if prediction == "FAIL" else "PROCEED"
    }

if __name__ == "__main__":
    print("Test Predictor Output:", predict_build_outcome(300.0, 0.05))
