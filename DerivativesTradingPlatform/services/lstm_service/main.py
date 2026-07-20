import os
import json
import numpy as np
import tensorflow as tf
from confluent_kafka import Consumer, Producer, KafkaError

# Configuration
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
MODEL_PATH = os.getenv("MODEL_PATH", "/models/lstm_demand_model.h5")
WINDOW_SIZE = 96  # 24 hours * 4 intervals per hour
NUM_FEATURES = 3  # [actual_mw, wind_speed_ms, solar_irradiance]

# Min-Max Normalization Constants (Example Values)
SCALER_MIN = np.array([0.0, 0.0, 0.0])
SCALER_MAX = np.array([200.0, 30.0, 1000.0])

def scale_features(raw_features):
    return (np.array(raw_features) - SCALER_MIN) / (SCALER_MAX - SCALER_MIN + 1e-8)

def descale_target(scaled_val):
    return scaled_val * (SCALER_MAX[0] - SCALER_MIN[0]) + SCALER_MIN[0]

# Load Trained Keras Model (if exists)
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
else:
    print(f"Warning: Model not found at {MODEL_PATH}, creating mock model")
    # Create a simple mock model for testing
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, input_shape=(WINDOW_SIZE, NUM_FEATURES)),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

# In-memory sliding window buffer per production region
region_buffers = {}

# Kafka Setup
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'lstm-inference-group',
    'auto.offset.reset': 'latest'
})
consumer.subscribe(['grid-consumption-raw'])

producer = Producer({'bootstrap.servers': KAFKA_BROKERS})

print("LSTM Inference Service Started. Listening for 15-minute ticks...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka Error: {msg.error()}")
                break

        # Parse Incoming Stream Metric
        data = json.loads(msg.value().decode('utf-8'))
        region = data['region_id']
        
        # Extract features
        features = [data['actual_mw'], data['wind_speed_ms'], data['solar_irradiance']]
        scaled = scale_features(features)

        # Update sliding window state
        if region not in region_buffers:
            region_buffers[region] = []
        
        region_buffers[region].append(scaled)
        
        # Enforce rolling 24-hour limit
        if len(region_buffers[region]) > WINDOW_SIZE:
            region_buffers[region].pop(0)

        # Run prediction if window state is fully ready
        if len(region_buffers[region]) == WINDOW_SIZE:
            # Prepare tensor array input shape: [Batch=1, TimeSteps=96, Features=3]
            input_tensor = np.array([region_buffers[region]], dtype=np.float32)
            
            # Executing forward inference pass
            scaled_prediction = model.predict(input_tensor, verbose=0)[0][0]
            predicted_mw = float(descale_target(scaled_prediction))

            # Publish Forecast Event payload
            outbound_payload = {
                "timestamp": data['timestamp'],
                "forecast_target_time": (np.datetime64(data['timestamp']) + np.timedelta64(15, 'm')).astype(str) + "Z",
                "region_id": region,
                "predicted_mw": round(predicted_mw, 2)
            }
            
            producer.produce(
                'demand-forecasts-15m',
                key=region.encode('utf-8'),
                value=json.dumps(outbound_payload).encode('utf-8')
            )
            producer.flush()
            print(f"Forecast published: {outbound_payload}")

except KeyboardInterrupt:
    print("\nShutting down LSTM service...")
finally:
    consumer.close()
