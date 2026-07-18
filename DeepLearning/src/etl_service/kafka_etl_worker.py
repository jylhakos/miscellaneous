"""
Kafka ETL Worker - Event-driven time-series data processing.

This worker:
1. Consumes raw sensor data from Kafka
2. Maintains sliding windows per device
3. Applies transformations (normalization, feature engineering)
4. Publishes prepared features for ML inference
"""

import json
import numpy as np
import logging
from typing import Dict, List
from confluent_kafka import Consumer, Producer, KafkaError
from collections import defaultdict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.etl_service.transform import transform_window

logger = setup_logger(__name__)

# Sliding window buffer per device (in-memory state)
device_buffers: Dict[str, List[float]] = defaultdict(list)

# Initialize Kafka consumer and producer
consumer = Consumer(Config.get_kafka_consumer_config('etl-group'))
producer = Producer(Config.get_kafka_producer_config())

# Subscribe to input topic
consumer.subscribe([Config.KAFKA_RAW_TOPIC])

logger.info(f"ETL Worker started. Consuming from '{Config.KAFKA_RAW_TOPIC}'...")
logger.info(f"Window size: {Config.WINDOW_SIZE}")


def delivery_report(err, msg):
    """Callback for producer delivery reports."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def send_to_dlq(device_id: str, original_message: str, error_reason: str):
    """
    Send malformed messages to Dead Letter Queue for later analysis.
    
    Args:
        device_id: Device identifier
        original_message: The original message that failed
        error_reason: Reason for failure
    """
    dlq_payload = {
        'device_id': device_id,
        'original_message': original_message,
        'error_reason': error_reason,
        'timestamp': str(np.datetime64('now'))
    }
    
    producer.produce(
        Config.KAFKA_DLQ_TOPIC,
        key=device_id.encode('utf-8'),
        value=json.dumps(dlq_payload).encode('utf-8')
    )
    producer.poll(0)
    logger.warning(f'Message sent to DLQ: {error_reason}')


def stream_etl():
    """Main ETL processing loop."""
    processed_count = 0
    error_count = 0
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug(f'Reached end of partition {msg.partition()}')
                else:
                    logger.error(f'Consumer error: {msg.error()}')
                continue
            
            # Parse incoming message
            try:
                raw_value = msg.value().decode('utf-8')
                data = json.loads(raw_value)
                device_id = data['device_id']
                value = float(data['value'])
                timestamp = data['timestamp']
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                error_count += 1
                logger.warning(f'Invalid message format: {e}')
                send_to_dlq('unknown', raw_value if 'raw_value' in locals() else 'undecodable', str(e))
                continue
            
            # Maintain chronologically ordered state in memory
            device_buffers[device_id].append(value)
            
            # Process once window is full
            if len(device_buffers[device_id]) >= Config.WINDOW_SIZE:
                # Extract latest window
                window_data = device_buffers[device_id][-Config.WINDOW_SIZE:]
                
                try:
                    # Apply ETL transformation
                    normalized = transform_window(window_data)
                    
                    # Structure feature payload for ML
                    feature_payload = {
                        "device_id": device_id,
                        "feature_vector": normalized.tolist(),
                        "latest_timestamp": timestamp,
                        "window_size": Config.WINDOW_SIZE
                    }
                    
                    # Publish to output topic
                    producer.produce(
                        Config.KAFKA_FEATURES_TOPIC,
                        key=device_id.encode('utf-8'),
                        value=json.dumps(feature_payload).encode('utf-8'),
                        callback=delivery_report
                    )
                    producer.poll(0)
                    
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        logger.info(f'Processed {processed_count} windows (errors: {error_count})')
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f'Transformation error for device {device_id}: {e}')
                    send_to_dlq(device_id, json.dumps(data), f'Transformation error: {e}')
                
                # Slide window by removing oldest value
                device_buffers[device_id] = device_buffers[device_id][1:]
                
    except KeyboardInterrupt:
        logger.info('ETL worker interrupted by user')
    finally:
        # Flush remaining messages and close connections
        logger.info(f'Final stats - Processed: {processed_count}, Errors: {error_count}')
        producer.flush()
        consumer.close()
        logger.info('ETL worker shut down gracefully')


if __name__ == "__main__":
    stream_etl()
