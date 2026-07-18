#!/usr/bin/env python3
"""
Produce sample sensor data to Kafka for testing the ETL pipeline.
"""

import json
import time
import random
from datetime import datetime, timedelta
from confluent_kafka import Producer
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def delivery_report(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}')


def generate_sensor_data(device_id: str, num_samples: int = 100):
    """
    Generate synthetic sensor data with trend and seasonality.
    
    Args:
        device_id: Unique device identifier
        num_samples: Number of samples to generate
    """
    producer = Producer(Config.get_kafka_producer_config())
    
    base_timestamp = datetime.now() - timedelta(hours=num_samples)
    base_value = 50.0
    
    logger.info(f"Generating {num_samples} samples for device {device_id}...")
    
    for i in range(num_samples):
        timestamp = base_timestamp + timedelta(hours=i)
        
        # Generate realistic sensor data with components:
        # - Trend: slow increase over time
        # - Seasonality: daily pattern
        # - Noise: random fluctuations
        trend = 0.05 * i
        seasonality = 10 * random.random() * (1 + 0.5 * (i % 24) / 24)
        noise = random.gauss(0, 2)
        
        value = base_value + trend + seasonality + noise
        
        event = {
            'device_id': device_id,
            'value': round(value, 2),
            'timestamp': timestamp.isoformat(),
            'metadata': {
                'sensor_type': 'temperature',
                'unit': 'celsius'
            }
        }
        
        # Produce to Kafka
        producer.produce(
            Config.KAFKA_RAW_TOPIC,
            key=device_id.encode('utf-8'),
            value=json.dumps(event).encode('utf-8'),
            callback=delivery_report
        )
        
        # Poll to handle delivery callbacks
        producer.poll(0)
        
        # Log progress
        if (i + 1) % 10 == 0:
            logger.info(f"Produced {i + 1}/{num_samples} messages")
        
        # Small delay to simulate real-time streaming
        time.sleep(0.1)
    
    # Wait for all messages to be delivered
    producer.flush()
    logger.info(f"Successfully produced {num_samples} messages for device {device_id}")


def main():
    """Main function to generate sample data for multiple devices."""
    devices = ['sensor-001', 'sensor-002', 'sensor-003']
    samples_per_device = 50
    
    logger.info("Starting sample data producer...")
    logger.info(f"Target topic: {Config.KAFKA_RAW_TOPIC}")
    logger.info(f"Kafka bootstrap servers: {Config.KAFKA_BOOTSTRAP_SERVERS}")
    
    try:
        for device_id in devices:
            generate_sensor_data(device_id, samples_per_device)
            time.sleep(1)  # Pause between devices
        
        logger.info("Sample data production completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Data production interrupted by user")
    except Exception as e:
        logger.error(f"Error producing sample data: {e}")
        raise


if __name__ == "__main__":
    main()
