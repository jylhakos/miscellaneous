# Makefile for Chat Service

.PHONY: help build run test clean docker docker-run deploy-gcp

# Variables
BINARY_NAME=chatservice
DOCKER_IMAGE=chatservice:latest
GO_FILES=$(shell find src -name "*.go")

# Default target
help:
	@echo "Available targets:"
	@echo "  build       - Build the application"
	@echo "  run         - Run the application locally"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean build artifacts"
	@echo "  docker      - Build Docker image"
	@echo "  docker-run  - Run with Docker Compose"
	@echo "  deploy-gcp  - Deploy to Google Cloud Platform"
	@echo "  test-api    - Test API endpoints"
	@echo "  setup-mongo - Set up local MongoDB"

# Build the application
build:
	@echo "Building $(BINARY_NAME)..."
	@cd src && go build -o ../$(BINARY_NAME) .

# Run the application
run: build
	@echo "Starting $(BINARY_NAME)..."
	@./$(BINARY_NAME)

# Run tests
test:
	@echo "Running tests..."
	@go test -v ./src/...

# Clean build artifacts
clean:
	@echo "Cleaning..."
	@rm -f $(BINARY_NAME)
	@go clean

# Build Docker image
docker:
	@echo "Building Docker image..."
	@docker build -t $(DOCKER_IMAGE) .

# Run with Docker Compose
docker-run:
	@echo "Starting services with Docker Compose..."
	@docker-compose up -d

# Deploy to GCP
deploy-gcp:
	@echo "Deploying to Google Cloud Platform..."
	@./scripts/deploy_gcp.sh

# Test API endpoints
test-api:
	@echo "Testing API endpoints..."
	@./scripts/test_api.sh

# Set up local MongoDB
setup-mongo:
	@echo "Setting up local MongoDB..."
	@docker run -d --name mongodb -p 27017:27017 mongo:7.0

# Install dependencies
deps:
	@echo "Installing dependencies..."
	@go mod download
	@go mod tidy

# Format code
fmt:
	@echo "Formatting code..."
	@go fmt ./src/...

# Lint code (requires golangci-lint)
lint:
	@echo "Linting code..."
	@golangci-lint run ./src/...

# Generate code coverage
coverage:
	@echo "Generating code coverage..."
	@go test -coverprofile=coverage.out ./src/...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

# Run development server with hot reload (requires air)
dev:
	@echo "Starting development server with hot reload..."
	@air -c .air.toml

# Stop Docker services
docker-stop:
	@echo "Stopping Docker services..."
	@docker-compose down

# View logs
logs:
	@docker-compose logs -f chatservice

# MongoDB shell
mongo-shell:
	@docker exec -it mongodb mongo chatservice