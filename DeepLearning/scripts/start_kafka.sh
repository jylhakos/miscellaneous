#!/bin/bash

# Start Kafka and create topics for the ML pipeline

set -e

echo "========================================="
echo "Starting Kafka Infrastructure"
echo "========================================="

# Start Kafka and Zookeeper
echo ""
echo "Starting Zookeeper and Kafka..."
docker-compose -f docker/docker-compose.yml up -d zookeeper kafka

# Wait for Kafka to be ready
echo ""
echo "Waiting for Kafka to be ready..."
sleep 15

# Check if Kafka is running
KAFKA_CONTAINER=$(docker ps -qf "name=kafka")
if [ -z "$KAFKA_CONTAINER" ]; then
    echo "Error: Kafka container is not running!"
    exit 1
fi

echo "Kafka is running."

# Create topics
echo ""
echo "Creating Kafka topics..."

# Raw sensor data topic
docker exec $KAFKA_CONTAINER kafka-topics \
    --create --if-not-exists \
    --topic raw-sensor-data \
    --bootstrap-server localhost:9092 \
    --partitions 6 \
    --replication-factor 1

# Prepared ML features topic
docker exec $KAFKA_CONTAINER kafka-topics \
    --create --if-not-exists \
    --topic prepared-ml-features \
    --bootstrap-server localhost:9092 \
    --partitions 6 \
    --replication-factor 1

# ML predictions topic
docker exec $KAFKA_CONTAINER kafka-topics \
    --create --if-not-exists \
    --topic ml-predictions \
    --bootstrap-server localhost:9092 \
    --partitions 6 \
    --replication-factor 1

# Dead letter queue topic
docker exec $KAFKA_CONTAINER kafka-topics \
    --create --if-not-exists \
    --topic raw-sensor-data-dlq \
    --bootstrap-server localhost:9092 \
    --partitions 3 \
    --replication-factor 1

# List all topics
echo ""
echo "Created topics:"
docker exec $KAFKA_CONTAINER kafka-topics \
    --list \
    --bootstrap-server localhost:9092

echo ""
echo "========================================="
echo "Kafka setup completed successfully!"
echo "========================================="
echo ""
echo "Bootstrap server: localhost:9092"
echo "Topics created: raw-sensor-data, prepared-ml-features, ml-predictions, raw-sensor-data-dlq"
