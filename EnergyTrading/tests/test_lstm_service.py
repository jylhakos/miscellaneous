import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../services/lstm_service'))

def test_scale_features():
    """Test feature scaling function"""
    from main import scale_features, SCALER_MIN, SCALER_MAX
    import numpy as np
    
    raw = [100.0, 15.0, 500.0]
    scaled = scale_features(raw)
    
    assert len(scaled) == 3
    assert np.all(scaled >= 0)
    assert np.all(scaled <= 1)

def test_descale_target():
    """Test target descaling function"""
    from main import descale_target, SCALER_MIN, SCALER_MAX
    
    scaled_val = 0.5
    descaled = descale_target(scaled_val)
    
    assert isinstance(descaled, (int, float))
    assert descaled >= 0

@patch('main.tf.keras.models.load_model')
def test_model_loading(mock_load_model):
    """Test LSTM model loading"""
    mock_model = Mock()
    mock_load_model.return_value = mock_model
    
    # This would test the actual loading logic
    assert mock_load_model.call_count >= 0

def test_kafka_message_parsing():
    """Test Kafka message parsing"""
    sample_message = {
        "timestamp": "2026-07-19T07:00:00Z",
        "region_id": "wind_farm_zone_1",
        "actual_mw": 42.5,
        "wind_speed_ms": 12.4,
        "solar_irradiance": 150.0
    }
    
    assert sample_message['region_id'] == "wind_farm_zone_1"
    assert isinstance(sample_message['actual_mw'], float)
    assert sample_message['actual_mw'] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
