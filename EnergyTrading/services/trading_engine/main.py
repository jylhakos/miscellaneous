import os
import json
from confluent_kafka import Consumer

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
IMBALANCE_THRESHOLD_MW = float(os.getenv("TRADING_THRESHOLD_MW", "2.5"))

# Dummy registry representing your fixed Day-Ahead forward sale delivery commitments
DAY_AHEAD_COMMITMENTS = {
    "wind_farm_zone_1": 40.0  # Enterprise committed to deliver 40 MW this hour
}

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'trading-strategy-group',
    'auto.offset.reset': 'latest'
})
consumer.subscribe(['demand-forecasts-15m'])

print("Trading Engine Online. Evaluating positions against Keras model updates...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        forecast = json.loads(msg.value().decode('utf-8'))
        region = forecast['region_id']
        predicted_generation = forecast['predicted_mw']
        
        committed_mw = DAY_AHEAD_COMMITMENTS.get(region, 0.0)
        imbalance = predicted_generation - committed_mw

        print(f"Region: {region} | Forecast: {predicted_generation}MW | Committed: {committed_mw}MW | Delta: {imbalance:.2f}MW")

        # Trading Financial Decisions Execution Logic
        if imbalance > IMBALANCE_THRESHOLD_MW:
            # Overproduction Risk: Extra power will drop Intraday Market clearing price.
            # Strategy: Short futures or buy puts immediately to protect asset revenue.
            print(f"[TRADE SIGNAL] ORDER -> SELL SHORT Intraday Derivative for {abs(imbalance):.2f} MW to hedge OVERPRODUCTION risk.")
            
        elif imbalance < -IMBALANCE_THRESHOLD_MW:
            # Underproduction Deficit Penalty Risk: Forced to purchase balancing grid penalties.
            # Strategy: Go Long on Intraday Hourly Options to secure replacement supply cheaply.
            print(f"[TRADE SIGNAL] ORDER -> BUY LONG Intraday Derivative for {abs(imbalance):.2f} MW to hedge UNDERPRODUCTION penalty.")

except KeyboardInterrupt:
    print("\nShutting down trading engine...")
finally:
    consumer.close()
