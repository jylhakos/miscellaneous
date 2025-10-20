#!/bin/bash

# API endpoint test scripts

# Create Message
create_message() {
    echo "Creating a message..."
    curl -X POST "http://localhost:8080/v1/messages" \
        -H "Content-Type: application/json" \
        -d '{
            "content": "Hello World!",
            "sender_id": "user123",
            "message_type": "text",
            "priority": "normal",
            "tags": ["greeting"]
        }'
}

# List Messages
list_messages() {
    echo "Listing messages..."
    curl -X GET "http://localhost:8080/v1/messages?page=1&limit=10"
}

# Get Message by ID
get_message() {
    if [ -z "$1" ]; then
        echo "Usage: get_message <message_id>"
        return 1
    fi
    echo "Getting message with ID: $1"
    curl -X GET "http://localhost:8080/v1/messages/$1"
}

# Delete Message
delete_message() {
    if [ -z "$1" ]; then
        echo "Usage: delete_message <message_id>"
        return 1
    fi
    echo "Deleting message with ID: $1"
    curl -X DELETE "http://localhost:8080/v1/messages/$1"
}

# Check Anomaly Score
check_anomaly() {
    if [ -z "$1" ]; then
        echo "Usage: check_anomaly <message_id>"
        return 1
    fi
    echo "Checking anomaly score for message ID: $1"
    curl -X GET "http://localhost:8080/v1/messages/$1/anomaly-check"
}

# Health Check
health_check() {
    echo "Checking service health..."
    curl -X GET "http://localhost:8080/health"
}

# Show usage
usage() {
    echo "Available commands:"
    echo "  create_message          - Create a new message"
    echo "  list_messages           - List all messages"
    echo "  get_message <id>        - Get message by ID"
    echo "  delete_message <id>     - Delete message by ID"
    echo "  check_anomaly <id>      - Check anomaly score"
    echo "  health_check            - Check service health"
}

# Execute function based on argument
case "$1" in
    "create")
        create_message
        ;;
    "list")
        list_messages
        ;;
    "get")
        get_message "$2"
        ;;
    "delete")
        delete_message "$2"
        ;;
    "anomaly")
        check_anomaly "$2"
        ;;
    "health")
        health_check
        ;;
    *)
        usage
        ;;
esac