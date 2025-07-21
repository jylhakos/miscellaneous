#!/bin/bash

# Redis Docker Management Script for LangChain Weather Agent
# Usage: ./redis-manager.sh [start|stop|restart|status|logs|clean|test]

set -e

CONTAINER_NAME="langchain-redis"
REDIS_IMAGE="redis:7-alpine"
REDIS_PORT="6379"

print_header() {
    echo " Redis Docker Manager for LangChain Weather Agent"
    echo "=================================================="
}

start_redis() {
    print_header
    echo " Starting Redis container..."
    
    # Check if container already exists
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            echo " Redis container is already running!"
            return 0
        else
            echo " Starting existing Redis container..."
            docker start ${CONTAINER_NAME}
        fi
    else
        echo " Creating new Redis container..."
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p ${REDIS_PORT}:6379 \
            -v redis-data:/data \
            ${REDIS_IMAGE} \
            redis-server --appendonly yes
    fi
    
    echo " Waiting for Redis to be ready..."
    sleep 3
    
    # Test connection
    if docker exec ${CONTAINER_NAME} redis-cli ping | grep -q "PONG"; then
        echo " Redis is running and responding at localhost:${REDIS_PORT}"
        echo " Connection string: redis://localhost:${REDIS_PORT}"
    else
        echo "❌ Redis is not responding properly"
        exit 1
    fi
}

stop_redis() {
    print_header
    echo "🛑 Stopping Redis container..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker stop ${CONTAINER_NAME}
        echo " Redis container stopped"
    else
        echo " Redis container is not running"
    fi
}

restart_redis() {
    print_header
    echo " Restarting Redis container..."
    stop_redis
    sleep 2
    start_redis
}

status_redis() {
    print_header
    echo " Redis Container Status:"
    
    if docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "^${CONTAINER_NAME}"; then
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -1
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "^${CONTAINER_NAME}"
        
        echo ""
        echo " Testing Redis connection..."
        if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            if docker exec ${CONTAINER_NAME} redis-cli ping 2>/dev/null | grep -q "PONG"; then
                echo " Redis is responding to ping"
                
                # Show some basic info
                echo ""
                echo "📈 Redis Info:"
                docker exec ${CONTAINER_NAME} redis-cli info server | grep "redis_version\|uptime_in_seconds\|connected_clients"
            else
                echo "❌ Redis is not responding to ping"
            fi
        else
            echo "❌ Redis container is not running"
        fi
    else
        echo "❌ Redis container does not exist"
        echo " Run './redis-manager.sh start' to create and start Redis"
    fi
}

logs_redis() {
    print_header
    echo " Redis Container Logs (last 50 lines):"
    echo "=========================================="
    
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        docker logs --tail 50 ${CONTAINER_NAME}
    else
        echo "❌ Redis container does not exist"
    fi
}

clean_redis() {
    print_header
    echo " Cleaning Redis container and data..."
    echo "⚠️  This will delete all stored Redis data!"
    
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Stop and remove container
        if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
            echo "🛑 Stopping and removing container..."
            docker stop ${CONTAINER_NAME} 2>/dev/null || true
            docker rm ${CONTAINER_NAME}
        fi
        
        # Remove volume
        echo " Removing Redis data volume..."
        docker volume rm redis-data 2>/dev/null || echo "ℹ️  Volume 'redis-data' does not exist"
        
        echo " Redis cleanup completed"
    else
        echo "❌ Operation cancelled"
    fi
}

test_redis() {
    print_header
    echo " Testing Redis functionality..."
    
    if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "❌ Redis container is not running"
        echo " Run './redis-manager.sh start' first"
        exit 1
    fi
    
    echo "1. Testing basic Redis operations..."
    docker exec ${CONTAINER_NAME} redis-cli set test:key "Hello Docker Redis!" > /dev/null
    RESULT=$(docker exec ${CONTAINER_NAME} redis-cli get test:key)
    
    if [ "$RESULT" = "Hello Docker Redis!" ]; then
        echo " SET/GET operations working"
    else
        echo "❌ SET/GET operations failed"
        exit 1
    fi
    
    echo "2. Testing expiry (TTL)..."
    docker exec ${CONTAINER_NAME} redis-cli setex test:ttl 5 "expires in 5 seconds" > /dev/null
    TTL=$(docker exec ${CONTAINER_NAME} redis-cli ttl test:ttl)
    
    if [ "$TTL" -gt 0 ]; then
        echo " TTL operations working (expires in ${TTL} seconds)"
    else
        echo "❌ TTL operations failed"
    fi
    
    echo "3. Testing Node.js connection..."
    if command -v node > /dev/null; then
        node test-redis.js
    else
        echo " Node.js not available for connection test"
    fi
    
    echo " Redis test completed successfully!"
}

show_help() {
    print_header
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start Redis container"
    echo "  stop      Stop Redis container"  
    echo "  restart   Restart Redis container"
    echo "  status    Show Redis container status"
    echo "  logs      Show Redis container logs"
    echo "  clean     Remove Redis container and data (destructive!)"
    echo "  test      Test Redis functionality"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 test"
    echo ""
}

# Main script logic
case "${1:-help}" in
    start)
        start_redis
        ;;
    stop)
        stop_redis
        ;;
    restart)
        restart_redis
        ;;
    status)
        status_redis
        ;;
    logs)
        logs_redis
        ;;
    clean)
        clean_redis
        ;;
    test)
        test_redis
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
