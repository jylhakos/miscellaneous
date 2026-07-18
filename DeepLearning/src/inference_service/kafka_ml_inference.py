"""
Kafka ML Inference Service - Real-time predictions using LSTM model.

This service:
1. Consumes prepared features from Kafka
2. Loads pre-trained LSTM model
3. Performs real-time inference
4. Publishes predictions back to Kafka
"""

import json
import numpy as np
import logging
import tensorflow as tf
from confluent_kafka import Consumer, Producer, KafkaError
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.inference_service.model_loader import ModelLoader

logger = setup_logger(__name__)

# Configure TensorFlow GPU settings
ModelLoader.configure_gpu_memory(memory_growth=True)

# Load pre-trained LSTM model
model_loader = ModelLoader(Config.MODEL_PATH)
try:
    model = model_loader.load_model()
    logger.info(f'Model loaded successfully from {Config.MODEL_PATH}')
    logger.info(f'Model input shape: {model.input_shape}')
    logger.info(f'Model output shape: {model.output_shape}')
except Exception as e:
    logger.error(f'Failed to load model: {e}')
    raise

# Initialize Kafka consumer and producer
consumer = Consumer(Config.get_kafka_consumer_config('ml-inference-group'))
producer = Producer(Config.get_kafka_producer_config())

consumer.subscribe([Config.KAFKA_FEATURES_TOPIC])

logger.info(f"ML Inference Service started. Consuming from '{Config.KAFKA_FEATURES_TOPIC}'...")


def delivery_report(err, msg):
    """Callback for producer delivery reports."""
    if err is not None:
        logger.error(f'Prediction delivery failed: {err}')
    else:
        logger.debug(f'Prediction delivered to {msg.topic()} [{msg.partition()}]')


def run_inference():
    """Main inference loop."""
    prediction_count = 0
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
            
            # Parse incoming feature payload
            try:
                payload = json.loads(msg.value().decode('utf-8'))
                device_id = payload['device_id']
                feature_vector = payload['feature_vector']
                timestamp = payload['latest_timestamp']
                window_size = payload['window_size']
            except (json.JSONDecodeError, KeyError) as e:
                error_count += 1
                logger.warning(f'Invalid payload format: {e}')
                continue
            
            # Reshape feature vector to match TensorFlow expected input
            # Shape: (batch_size, time_steps, features) -> (1, window_size, 1)
            try:
                feature_array = np.array(feature_vector, dtype=np.float32).reshape(1, window_size, 1)
            except ValueError as e:
                error_count += 1
                logger.warning(f'Invalid feature vector shape for device {device_id}: {e}')
                continue
            
            # Execute model prediction
            try:
                prediction = model.predict(feature_array, verbose=0)
                predicted_value = float(prediction[0][0])
                
                # Publish prediction back to Kafka
                inference_result = {
                    "device_id": device_id,
                    "predicted_value": predicted_value,
                    "timestamp": timestamp,
                    "model_version": Config.MODEL_VERSION
                }
                
                producer.produce(
                    Config.KAFKA_PREDICTIONS_TOPIC,
                    key=device_id.encode('utf-8'),
                    value=json.dumps(inference_result).encode('utf-8'),
                    callback=delivery_report
                )
                producer.poll(0)
                
                prediction_count += 1
                
                if prediction_count % 10 == 0:
                    logger.info(f'Generated {prediction_count} predictions (errors: {error_count})')
                else:
                    logger.debug(f'Prediction for device {device_id}: {predicted_value:.4f}')
                
            except Exception as e:
                error_count += 1
                logger.error(f'Inference error for device {device_id}: {e}')
            
    except KeyboardInterrupt:
        logger.info('Inference service interrupted by user')
    finally:
        logger.info(f'Final stats - Predictions: {prediction_count}, Errors: {error_count}')
        producer.flush()
        consumer.close()
        logger.info('Inference service shut down gracefully')


if __name__ == "__main__":
    run_inference()
