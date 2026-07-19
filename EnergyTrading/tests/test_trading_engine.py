import pytest
import json
import sys
import os

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../services/trading_engine'))

def test_imbalance_calculation():
    """Test imbalance calculation logic"""
    predicted_generation = 44.0
    committed_mw = 40.0
    imbalance = predicted_generation - committed_mw
    
    assert imbalance == 4.0
    assert imbalance > 0  # Overproduction

def test_trading_signal_overproduction():
    """Test trading signal for overproduction scenario"""
    IMBALANCE_THRESHOLD_MW = 2.5
    imbalance = 5.0
    
    if imbalance > IMBALANCE_THRESHOLD_MW:
        signal = "SELL_SHORT"
    else:
        signal = "HOLD"
    
    assert signal == "SELL_SHORT"

def test_trading_signal_underproduction():
    """Test trading signal for underproduction scenario"""
    IMBALANCE_THRESHOLD_MW = 2.5
    imbalance = -5.0
    
    if imbalance < -IMBALANCE_THRESHOLD_MW:
        signal = "BUY_LONG"
    else:
        signal = "HOLD"
    
    assert signal == "BUY_LONG"

def test_trading_signal_balanced():
    """Test trading signal for balanced scenario"""
    IMBALANCE_THRESHOLD_MW = 2.5
    imbalance = 1.0
    
    if imbalance > IMBALANCE_THRESHOLD_MW:
        signal = "SELL_SHORT"
    elif imbalance < -IMBALANCE_THRESHOLD_MW:
        signal = "BUY_LONG"
    else:
        signal = "HOLD"
    
    assert signal == "HOLD"

def test_forecast_message_structure():
    """Test forecast message structure"""
    forecast = {
        "timestamp": "2026-07-19T07:00:00Z",
        "forecast_target_time": "2026-07-19T07:15:00Z",
        "region_id": "wind_farm_zone_1",
        "predicted_mw": 44.1
    }
    
    assert 'predicted_mw' in forecast
    assert 'region_id' in forecast
    assert isinstance(forecast['predicted_mw'], float)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
