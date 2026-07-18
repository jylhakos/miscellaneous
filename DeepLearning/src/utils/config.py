"""Configuration management using environment variables."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for accessing environment variables."""
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_RAW_TOPIC: str = os.getenv('KAFKA_RAW_TOPIC', 'raw-sensor-data')
    KAFKA_FEATURES_TOPIC: str = os.getenv('KAFKA_FEATURES_TOPIC', 'prepared-ml-features')
    KAFKA_PREDICTIONS_TOPIC: str = os.getenv('KAFKA_PREDICTIONS_TOPIC', 'ml-predictions')
    KAFKA_DLQ_TOPIC: str = os.getenv('KAFKA_DLQ_TOPIC', 'raw-sensor-data-dlq')
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB: int = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD: Optional[str] = os.getenv('REDIS_PASSWORD', None)
    
    # Model Configuration
    MODEL_PATH: str = os.getenv('MODEL_PATH', 'models/time_series_lstm.keras')
    MODEL_VERSION: str = os.getenv('MODEL_VERSION', '1.0')
    WINDOW_SIZE: int = int(os.getenv('WINDOW_SIZE', '24'))
    
    # Service Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '32'))
    PREDICTION_TIMEOUT: int = int(os.getenv('PREDICTION_TIMEOUT', '5'))
    
    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    AWS_S3_BUCKET: Optional[str] = os.getenv('AWS_S3_BUCKET', None)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    
    @classmethod
    def get_kafka_consumer_config(cls, group_id: str) -> dict:
        """Get Kafka consumer configuration."""
        return {
            'bootstrap.servers': cls.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': group_id,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True
        }
    
    @classmethod
    def get_kafka_producer_config(cls) -> dict:
        """Get Kafka producer configuration."""
        return {
            'bootstrap.servers': cls.KAFKA_BOOTSTRAP_SERVERS,
            'acks': 'all',
            'retries': 3
        }
