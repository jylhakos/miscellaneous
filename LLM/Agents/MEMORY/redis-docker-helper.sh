# Redis Setup Scripts

## Start Redis with Docker Compose
start_redis() {
    echo " Starting Redis with Docker Compose..."
    docker-compose up -d redis
    echo " Waiting for Redis to be ready..."
    sleep 5
    docker-compose ps redis
    echo " Redis should be running on localhost:6379"
}

## Stop Redis
stop_redis() {
    echo "🛑 Stopping Redis container..."
    docker-compose down
}

## Check Redis status
check_redis() {
    echo " Checking Redis status..."
    docker-compose ps redis
    echo " Testing Redis connection..."
    docker exec langchain-redis redis-cli ping || echo "❌ Redis not responding"
}

## Clean Redis data (careful!)
clean_redis() {
    echo " Cleaning Redis data (this will delete all stored data)..."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        echo " Redis data cleaned"
    else
        echo "❌ Operation cancelled"
    fi
}

# Export functions for use
export -f start_redis stop_redis check_redis clean_redis

echo " Redis Docker helper functions loaded!"
echo "Available commands:"
echo "  start_redis  - Start Redis container"
echo "  stop_redis   - Stop Redis container" 
echo "  check_redis  - Check Redis status"
echo "  clean_redis  - Clean Redis data (destructive!)"
