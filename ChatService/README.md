# Chat Service

API service for storing and retrieving chat messages built with Go, Gin framework, and MongoDB.

## Features

- RESTful API for chat message CRUD operations
- MongoDB integration with optimized queries
- Anomaly detection for spam messages
- Rate limiting and security middleware
- JWT authentication support
- CORS enabled
- Docker containerization
- Horizontal scaling ready
- Logging and monitoring

## Architecture

```
src/
├── config/          # Configuration management
├── handlers/        # HTTP request handlers
├── middleware/      # Custom middleware (CORS, JWT, Rate limiting)
├── models/          # Data models and structures
├── services/        # Business logic layer
└── main.go          # Application entry point
```

## Endpoints (API)

### Health Check
- `GET /health` - Service health status

### Messages
- `POST /v1/messages` - Create a new message
- `GET /v1/messages` - List messages with pagination
- `GET /v1/messages/{id}` - Get specific message by ID
- `DELETE /v1/messages/{id}` - Delete message by ID
- `GET /v1/messages/{id}/anomaly-check` - Get anomaly score for spam detection

## Quick Start

### Prerequisites

- Go 1.21 or higher
- MongoDB 7.0 or higher
- Docker and Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChatService
   ```

2. **Install dependencies**
   ```bash
   go mod download
   ```

3. **Set up MongoDB locally**
   ```bash
   # Install MongoDB (Ubuntu/Debian)
   wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   
   # Start MongoDB service
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

4. **Configure environment variables**
   ```bash
   export MONGODB_URI="mongodb://localhost:27017"
   export MONGODB_DATABASE="chatservice"
   export MONGODB_COLLECTION="messages"
   export SERVER_PORT="8080"
   export JWT_SECRET_KEY="your-secret-key-change-in-production"
   ```

5. **Run the application**
   ```bash
   cd src
   go run main.go
   ```

### Docker Setup

1. **Using Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

2. **Build and run manually**
   ```bash
   # Build the image
   docker build -t chatservice .
   
   # Run with MongoDB
   docker run -d --name mongodb mongo:7.0
   docker run -d --name chatservice -p 8080:8080 --link mongodb:mongodb \
     -e MONGODB_URI=mongodb://mongodb:27017 chatservice
   ```

## Testing the API

### Using curl scripts

1. **Run comprehensive tests**
   ```bash
   ./scripts/test_api.sh
   ```

2. **Individual endpoint tests**
   ```bash
   # Create a message
   ./scripts/curl_commands.sh create
   
   # List messages
   ./scripts/curl_commands.sh list
   
   # Get message by ID
   ./scripts/curl_commands.sh get <message_id>
   
   # Check anomaly score
   ./scripts/curl_commands.sh anomaly <message_id>
   
   # Delete message
   ./scripts/curl_commands.sh delete <message_id>
   
   # Health check
   ./scripts/curl_commands.sh health
   ```

### Manual curl examples

1. **Create a message**
   ```bash
   curl -X POST "http://localhost:8080/v1/messages" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Hello World!",
       "sender_id": "user123",
       "message_type": "text",
       "priority": "normal",
       "tags": ["greeting"]
     }'
   ```

2. **List messages with pagination**
   ```bash
   curl -X GET "http://localhost:8080/v1/messages?page=1&limit=10"
   ```

3. **Get message by ID**
   ```bash
   curl -X GET "http://localhost:8080/v1/messages/{message_id}"
   ```

4. **Delete message**
   ```bash
   curl -X DELETE "http://localhost:8080/v1/messages/{message_id}"
   ```

5. **Check anomaly score**
   ```bash
   curl -X GET "http://localhost:8080/v1/messages/{message_id}/anomaly-check"
   ```

## Configuration

The application supports configuration through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| MONGODB_URI | mongodb://localhost:27017 | MongoDB connection string |
| MONGODB_DATABASE | chatservice | Database name |
| MONGODB_COLLECTION | messages | Collection name |
| SERVER_PORT | 8080 | Server port |
| SERVER_HOST | 0.0.0.0 | Server host |
| JWT_SECRET_KEY | your-secret-key-change-in-production | JWT signing key |
| JWT_ISSUER | chatservice | JWT issuer |
| JWT_EXPIRY_HOURS | 24 | JWT token expiry |
| RATE_LIMIT_RPM | 100 | Requests per minute limit |
| RATE_LIMIT_BURST | 10 | Rate limit burst size |

## Deployment

### Google Cloud Platform (GCP)

1. **Prepare the application**
   ```bash
   # Build for Linux
   GOOS=linux GOARCH=amd64 go build -o main ./src
   ```

2. **Create GCP project and enable services**
   ```bash
   gcloud projects create chatservice-project
   gcloud config set project chatservice-project
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable run.googleapis.com
   ```

3. **Build and push Docker image**
   ```bash
   # Tag and push to GCR
   docker build -t gcr.io/chatservice-project/chatservice .
   docker push gcr.io/chatservice-project/chatservice
   ```

4. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy chatservice \
     --image gcr.io/chatservice-project/chatservice \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars MONGODB_URI=mongodb://your-mongodb-atlas-uri
   ```

### IAM Roles and Security

1. **Required IAM roles for deployment**
   ```bash
   # Service Account for Cloud Run
   gcloud iam service-accounts create chatservice-sa
   
   # Grant necessary roles
   gcloud projects add-iam-policy-binding chatservice-project \
     --member="serviceAccount:chatservice-sa@chatservice-project.iam.gserviceaccount.com" \
     --role="roles/cloudsql.client"
   ```

2. **Security**
   - CORS middleware for cross-origin requests
   - Rate limiting to prevent abuse
   - Input validation and sanitization
   - Security headers (XSS protection, content type options)
   - JWT authentication support
   - HTTPS enforcement in production

## Performance and Scaling

### Horizontal Scaling

The application is designed for horizontal scaling:

1. **Stateless** - No server-side sessions
2. **Database connection pooling** - Efficient MongoDB connections
3. **Load balancer** - Health check endpoint available
4. **Docker containerization** - Easy deployment and scaling

### Scaling with Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatservice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatservice
  template:
    metadata:
      labels:
        app: chatservice
    spec:
      containers:
      - name: chatservice
        image: gcr.io/chatservice-project/chatservice
        ports:
        - containerPort: 8080
        env:
        - name: MONGODB_URI
          value: "mongodb://mongodb-service:27017"
```

### Performance Optimizations

- MongoDB indexes on frequently queried fields
- Connection pooling for database connections
- Efficient pagination for large datasets
- Rate limiting to protect against abuse
- Middleware for request/response compression

## Development

### Building the application

```bash
# Development build
go build -o chatservice ./src

# Production build with optimizations
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o chatservice ./src
```

### Running tests

```bash
# Run unit tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

### Code formatting and linting

```bash
# Format code
go fmt ./...

# Run linter (install golangci-lint first)
golangci-lint run
```

## Git Workflow

### Creating a git bundle

```bash
# Create a bundle with all branches and history
git bundle create chatservice.bundle --all

# Create a bundle for specific branch
git bundle create chatservice-main.bundle main

# Verify bundle
git bundle verify chatservice.bundle
```

### Using git bundle

```bash
# Clone from bundle
git clone chatservice.bundle chatservice-from-bundle

# Fetch from bundle
git remote add bundle chatservice.bundle
git fetch bundle
```

### Git commands

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Add new feature"

# Create and switch to new branch
git checkout -b feature/new-feature

# Merge branch
git checkout main
git merge feature/new-feature

# Push changes
git push origin main

# Pull latest changes
git pull origin main

# View commit history
git log --oneline --graph

# View differences
git diff
git diff --staged
```

## MongoDB Setup

### Local MongoDB Installation

```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### MongoDB Atlas (Cloud)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Configure network access and database user
4. Get connection string and update MONGODB_URI

### Database Indexes

The application creates these indexes for optimal performance:

```javascript
// Timestamp index for sorting messages by date
db.messages.createIndex({ "timestamp": -1 });

// Sender ID index for user-specific queries
db.messages.createIndex({ "sender_id": 1 });

// Message type index for filtering
db.messages.createIndex({ "metadata.message_type": 1 });
```

## Monitoring and Logging

### Application Logs

The application provides structured logging:
- Request/response logging
- Error logging with stack traces
- Performance metrics
- Security events

### Health Monitoring

```bash
# Check service health
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## Troubleshooting

### Issues

1. **MongoDB connection failed**
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod
   
   # Check connection string
   mongo mongodb://localhost:27017
   ```

2. **Port already in use**
   ```bash
   # Find process using port 8080
   sudo netstat -tlnp | grep :8080
   
   # Kill process
   sudo kill -9 <PID>
   ```

3. **Permission denied**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh
   ```

### Logs Location

- Application logs: stdout/stderr
- MongoDB logs: `/var/log/mongodb/mongod.log`
- Docker logs: `docker logs <container_name>`

## License

This project is licensed under the MIT License.
