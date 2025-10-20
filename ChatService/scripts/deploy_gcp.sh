#!/bin/bash

# GCP Deployment Script for Chat Service
set -e

# Configuration
PROJECT_ID="chatservice-project"
SERVICE_NAME="chatservice"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "===== Chat Service GCP Deployment ====="

# Check if required tools are installed
check_tools() {
    echo "Checking required tools..."
    command -v gcloud >/dev/null 2>&1 || { echo "gcloud CLI is required but not installed. Aborting." >&2; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
    echo "✓ All required tools are installed"
}

# Set up GCP project
setup_gcp() {
    echo "Setting up GCP project..."
    
    # Create project if it doesn't exist
    if ! gcloud projects describe $PROJECT_ID >/dev/null 2>&1; then
        echo "Creating project: $PROJECT_ID"
        gcloud projects create $PROJECT_ID
    fi
    
    # Set current project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    echo "Enabling required APIs..."
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    
    echo "✓ GCP project setup complete"
}

# Build and push Docker image
build_and_push() {
    echo "Building and pushing Docker image..."
    
    # Build the image
    docker build -f Dockerfile.prod -t $IMAGE_NAME .
    
    # Configure Docker to use gcloud as credential helper
    gcloud auth configure-docker
    
    # Push the image
    docker push $IMAGE_NAME
    
    echo "✓ Docker image built and pushed successfully"
}

# Deploy to Cloud Run
deploy_cloud_run() {
    echo "Deploying to Cloud Run..."
    
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8080 \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --set-env-vars "MONGODB_URI=${MONGODB_URI:-mongodb://localhost:27017}" \
        --set-env-vars "MONGODB_DATABASE=${MONGODB_DATABASE:-chatservice}" \
        --set-env-vars "JWT_SECRET_KEY=${JWT_SECRET_KEY:-change-me-in-production}" \
        --set-env-vars "RATE_LIMIT_RPM=100" \
        --set-env-vars "RATE_LIMIT_BURST=10"
    
    echo "✓ Deployment to Cloud Run complete"
}

# Get service URL
get_service_url() {
    echo "Getting service URL..."
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
    echo "Service deployed at: $SERVICE_URL"
    echo "Health check: $SERVICE_URL/health"
}

# Test deployment
test_deployment() {
    echo "Testing deployment..."
    if [ -n "$SERVICE_URL" ]; then
        echo "Testing health endpoint..."
        curl -f "$SERVICE_URL/health" || echo "Health check failed"
    fi
}

# Main execution
main() {
    echo "Starting deployment process..."
    
    check_tools
    setup_gcp
    build_and_push
    deploy_cloud_run
    get_service_url
    test_deployment
    
    echo "===== Deployment Complete ====="
    echo "Your Chat Service is now running at: $SERVICE_URL"
    echo ""
    echo "Next steps:"
    echo "1. Update your MongoDB connection string if using Atlas"
    echo "2. Configure custom domain if needed"
    echo "3. Set up monitoring and logging"
    echo "4. Test the API endpoints"
}

# Handle command line arguments
case "${1:-deploy}" in
    "setup")
        check_tools
        setup_gcp
        ;;
    "build")
        build_and_push
        ;;
    "deploy")
        main
        ;;
    *)
        echo "Usage: $0 [setup|build|deploy]"
        echo "  setup  - Set up GCP project and enable APIs"
        echo "  build  - Build and push Docker image"
        echo "  deploy - Full deployment (default)"
        ;;
esac