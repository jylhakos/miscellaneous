import os
import json
import requests
from confluent_kafka import Producer
from datetime import datetime
import time

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
NORD_POOL_API = "https://data.nordpoolgroup.com/auction/day-ahead/prices"
POLL_INTERVAL = 900  # 15 minutes

producer = Producer({'bootstrap.servers': KAFKA_BROKERS})

def fetch_market_data(region="FI"):
    """Fetch latest Nord Pool pricing data"""
    params = {
        'deliveryDate': 'latest',
        'currency': 'EUR',
        'aggregation': 'DeliveryPeriod',
        'deliveryAreas': region
    }
    try:
        response = requests.get(NORD_POOL_API, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def fetch_scada_telemetry():
    """Simulate SCADA system telemetry"""
    # In production, connect to actual MQTT broker
    import random
    return {
        'actual_mw': round(random.uniform(35.0, 50.0), 2),
        'wind_speed_ms': round(random.uniform(8.0, 18.0), 2),
        'solar_irradiance': round(random.uniform(0.0, 800.0), 2)
    }

def publish_to_kafka(topic, key, payload):
    """Publish message to Kafka topic"""
    try:
        producer.produce(
            topic,
            key=key.encode('utf-8'),
            value=json.dumps(payload).encode('utf-8')
        )
        producer.flush()
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")

print("Data Ingestion Service Started")

while True:
    try:
        # Collect telemetry
        telemetry = fetch_scada_telemetry()
        
        # Construct payload
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "region_id": "wind_farm_zone_1",
            "actual_mw": telemetry['actual_mw'],
            "wind_speed_ms": telemetry['wind_speed_ms'],
            "solar_irradiance": telemetry['solar_irradiance']
        }
        
        # Publish to Kafka
        publish_to_kafka('grid-consumption-raw', payload['region_id'], payload)
        print(f"Published: {payload}")
        
        time.sleep(POLL_INTERVAL)
        
    except KeyboardInterrupt:
        print("\nShutting down ingestion service...")
        break
    except Exception as e:
        print(f"Error in ingestion loop: {e}")
        time.sleep(60)
