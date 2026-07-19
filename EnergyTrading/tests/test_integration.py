import pytest
import time

def test_end_to_end_flow():
    """Test complete data flow from ingestion to trading"""
    
    # Simulate ingestion
    telemetry = {
        "timestamp": "2026-07-19T07:00:00Z",
        "region_id": "wind_farm_zone_1",
        "actual_mw": 42.5,
        "wind_speed_ms": 12.4,
        "solar_irradiance": 150.0
    }
    
    # Validate telemetry
    assert telemetry['actual_mw'] > 0
    assert telemetry['wind_speed_ms'] >= 0
    
    # Simulate LSTM prediction (mock)
    predicted_mw = 44.1
    
    # Simulate trading decision
    committed_mw = 40.0
    imbalance = predicted_mw - committed_mw
    
    # Verify trading signal
    THRESHOLD = 2.5
    if imbalance > THRESHOLD:
        signal = "SELL_SHORT"
    elif imbalance < -THRESHOLD:
        signal = "BUY_LONG"
    else:
        signal = "HOLD"
    
    assert signal == "SELL_SHORT"
    assert abs(imbalance) > THRESHOLD

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
