"""
Configuration module for Water Quality Time-Series Forecasting System
Centralized configuration management for all microservices
"""

import os


class Config:
    """Base configuration class"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', '192.168.3.2')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'demo')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'demo')
    DB_NAME = os.getenv('DB_NAME', 'demo')
    DB_URI = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    
    # MQTT Configuration
    MQTT_BROKER = os.getenv('MQTT_BROKER', '114.55.211.112')
    MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
    MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'api/v1/json/uploadmessage')
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'iot')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'iot')
    
    # ZeroMQ Configuration
    ZMQ_INPUT_PORT = int(os.getenv('ZMQ_INPUT_PORT', '5548'))
    ZMQ_OUTPUT_PORTS = [5561, 5562, 5563, 5564]
    
    # Model Configuration
    MODEL_FOLDER = os.getenv('MODEL_FOLDER', 'MODEL')
    TIME_WINDOW = int(os.getenv('TIME_WINDOW', '8'))  # Number of time steps for input
    PREDICTION_HORIZON = int(os.getenv('PREDICTION_HORIZON', '1'))  # Steps ahead to predict
    MIN_INPUT_LENGTH = int(os.getenv('MIN_INPUT_LENGTH', '8'))
    
    # Features Configuration
    FEATURE_LIST = [
        'ai_cod1_cod',  # Chemical Oxygen Demand
        'ai_ph1_temp',  # Temperature
        'ai_ph1_ph',    # pH level
        'ai_ss1_ss'     # Suspended Solids
    ]
    
    # TensorFlow/GPU Configuration
    GPU_MEMORY_FRACTION = float(os.getenv('GPU_MEMORY_FRACTION', '0.5'))
    GPU_ALLOW_GROWTH = os.getenv('GPU_ALLOW_GROWTH', 'True').lower() == 'true'
    NUM_GPU = int(os.getenv('NUM_GPU', '1'))
    NUM_CPU = int(os.getenv('NUM_CPU', '1'))
    NUM_CORES = int(os.getenv('NUM_CORES', '8'))
    
    # Service Configuration
    WEB_APP_PORT = int(os.getenv('WEB_APP_PORT', '3001'))
    UPDATE_INTERVAL_MS = int(os.getenv('UPDATE_INTERVAL_MS', '1000'))
    
    # Table Names
    INPUT_TABLE = 'water_input'
    OUTPUT_TABLE = 'water_output'
    DEVICES_TABLE = 'water_devices'
    
    # Data Collection
    TIMESTAMP_KEY = 'dataTime'
    IGNORE_PAYLOAD = 'clientOffline'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate configuration parameters"""
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing = [var for var in required_vars if not getattr(cls, var, None)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        return True


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    GPU_MEMORY_FRACTION = 0.7


# Select configuration based on environment
ENV = os.getenv('APP_ENV', 'development').lower()
if ENV == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
