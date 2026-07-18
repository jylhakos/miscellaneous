"""
Unit tests for model loading and inference.
"""

import pytest
import numpy as np
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.lstm_model import build_lstm_model
from src.inference_service.model_loader import ModelLoader


class TestModelInference:
    """Test suite for model loading and inference."""
    
    def test_build_lstm_model(self):
        """Test LSTM model building."""
        window_size = 24
        features = 1
        
        model = build_lstm_model(window_size, features)
        
        assert model is not None
        assert model.input_shape == (None, window_size, features)
        assert model.output_shape == (None, 1)
    
    def test_model_save_load(self):
        """Test model saving and loading."""
        window_size = 24
        
        # Build model
        model = build_lstm_model(window_size)
        
        # Save to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model.keras')
            model.save(model_path)
            
            # Load model
            loader = ModelLoader(model_path)
            loaded_model = loader.load_model()
            
            assert loaded_model is not None
            assert loaded_model.input_shape == model.input_shape
    
    def test_model_prediction(self):
        """Test model prediction."""
        window_size = 24
        
        # Build and compile model
        model = build_lstm_model(window_size)
        
        # Create sample input
        sample_input = np.random.randn(1, window_size, 1).astype(np.float32)
        
        # Make prediction
        prediction = model.predict(sample_input, verbose=0)
        
        assert prediction.shape == (1, 1)
        assert isinstance(prediction[0][0], (float, np.floating))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
