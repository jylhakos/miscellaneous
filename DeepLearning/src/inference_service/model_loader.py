"""Model loading and management utilities."""

import tensorflow as tf
from typing import Optional
import os


class ModelLoader:
    """Handles loading and caching of TensorFlow/Keras models."""
    
    def __init__(self, model_path: str):
        """
        Initialize model loader.
        
        Args:
            model_path: Path to the saved model file
        """
        self.model_path = model_path
        self.model: Optional[tf.keras.Model] = None
    
    def load_model(self) -> tf.keras.Model:
        """
        Load Keras model from disk.
        
        Returns:
            Loaded Keras model
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            return self.model
        except Exception as e:
            raise Exception(f"Failed to load model from {self.model_path}: {e}")
    
    def get_model(self) -> tf.keras.Model:
        """
        Get cached model or load if not already loaded.
        
        Returns:
            Keras model instance
        """
        if self.model is None:
            self.load_model()
        return self.model
    
    @staticmethod
    def configure_gpu_memory(memory_growth: bool = True, memory_limit_mb: Optional[int] = None):
        """
        Configure TensorFlow GPU memory settings.
        
        Args:
            memory_growth: Enable memory growth to avoid grabbing all GPU memory
            memory_limit_mb: Optional memory limit in MB
        """
        gpus = tf.config.list_physical_devices('GPU')
        
        if not gpus:
            return
        
        try:
            for gpu in gpus:
                if memory_growth:
                    tf.config.experimental.set_memory_growth(gpu, True)
                
                if memory_limit_mb:
                    tf.config.set_logical_device_configuration(
                        gpu,
                        [tf.config.LogicalDeviceConfiguration(memory_limit=memory_limit_mb)]
                    )
        except RuntimeError as e:
            # GPU configuration must be set before initializing TensorFlow
            print(f"GPU configuration error: {e}")
