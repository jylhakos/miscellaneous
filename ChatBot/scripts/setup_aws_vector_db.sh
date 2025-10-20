#!/bin/bash

# AWS Vector Database Setup Script for RAG Chatbot
# Sets up OpenSearch Service for production vector search

set -e

# Configuration
STACK_NAME="rag-chatbot-vector"
REGION="${AWS_REGION:-us-east-1}"
OPENSEARCH_DOMAIN_NAME="rag-chatbot-search"
OPENSEARCH_VERSION="OpenSearch_1.3"
INSTANCE_TYPE="t3.small.search"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}    AWS Vector Database Setup for RAG${NC}"
    echo -e "${BLUE}================================================${NC}"
}

# Function to check AWS CLI
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "AWS CLI is configured."
}

# Function to deploy OpenSearch domain
deploy_opensearch() {
    print_status "Deploying OpenSearch domain for vector search..."
    
    # Create CloudFormation template for OpenSearch
    cat > opensearch-template.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Description: 'OpenSearch Service domain for RAG vector search'

Parameters:
  DomainName:
    Type: String
    Default: rag-chatbot-search
    Description: Name for the OpenSearch domain
  
  InstanceType:
    Type: String
    Default: t3.small.search
    Description: Instance type for OpenSearch nodes
  
  VolumeSize:
    Type: Number
    Default: 20
    Description: EBS volume size in GB

Resources:
  OpenSearchServiceDomain:
    Type: AWS::OpenSearch::Domain
    Properties:
      DomainName: !Ref DomainName
      EngineVersion: 'OpenSearch_1.3'
      ClusterConfig:
        InstanceType: !Ref InstanceType
        InstanceCount: 1
        DedicatedMasterEnabled: false
      EBSOptions:
        EBSEnabled: true
        VolumeType: gp3
        VolumeSize: !Ref VolumeSize
      AccessPolicies:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub '${AWS::AccountId}'
            Action: 'es:*'
            Resource: !Sub 'arn:aws:es:${AWS::Region}:${AWS::AccountId}:domain/${DomainName}/*'
      DomainEndpointOptions:
        EnforceHTTPS: true
      NodeToNodeEncryptionOptions:
        Enabled: true
      EncryptionAtRestOptions:
        Enabled: true

Outputs:
  DomainEndpoint:
    Description: OpenSearch domain endpoint
    Value: !GetAtt OpenSearchServiceDomain.DomainEndpoint
    Export:
      Name: !Sub '${AWS::StackName}-DomainEndpoint'
  
  DomainArn:
    Description: OpenSearch domain ARN
    Value: !GetAtt OpenSearchServiceDomain.DomainArn
    Export:
      Name: !Sub '${AWS::StackName}-DomainArn'
EOF

    # Deploy the CloudFormation stack
    aws cloudformation deploy \
        --template-file opensearch-template.yaml \
        --stack-name $STACK_NAME \
        --parameter-overrides \
            DomainName=$OPENSEARCH_DOMAIN_NAME \
            InstanceType=$INSTANCE_TYPE \
        --region $REGION \
        --capabilities CAPABILITY_IAM
    
    print_status "OpenSearch domain deployment initiated"
    
    # Wait for the domain to be active
    print_status "Waiting for OpenSearch domain to become active..."
    aws opensearch wait domain-available \
        --domain-name $OPENSEARCH_DOMAIN_NAME \
        --region $REGION
    
    print_status "OpenSearch domain is now active"
    
    # Get domain endpoint
    DOMAIN_ENDPOINT=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`DomainEndpoint`].OutputValue' \
        --output text)
    
    print_status "OpenSearch endpoint: https://$DOMAIN_ENDPOINT"
    
    # Clean up template file
    rm opensearch-template.yaml
}

# Function to create vector index
create_vector_index() {
    print_status "Creating vector index in OpenSearch..."
    
    # Get domain endpoint
    DOMAIN_ENDPOINT=$(aws opensearch describe-domain \
        --domain-name $OPENSEARCH_DOMAIN_NAME \
        --region $REGION \
        --query 'DomainStatus.Endpoint' \
        --output text)
    
    if [ "$DOMAIN_ENDPOINT" = "None" ] || [ -z "$DOMAIN_ENDPOINT" ]; then
        print_error "Could not get OpenSearch domain endpoint"
        return 1
    fi
    
    # Create index with vector mapping
    curl -X PUT "https://$DOMAIN_ENDPOINT/rag-vectors" \
        -H "Content-Type: application/json" \
        -d '{
            "settings": {
                "index": {
                    "knn": true,
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            },
            "mappings": {
                "properties": {
                    "text": {
                        "type": "text"
                    },
                    "metadata": {
                        "type": "object"
                    },
                    "vector": {
                        "type": "knn_vector",
                        "dimension": 384,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib"
                        }
                    }
                }
            }
        }'
    
    print_status "Vector index created successfully"
}

# Function to test OpenSearch connection
test_opensearch() {
    print_status "Testing OpenSearch connection..."
    
    # Get domain endpoint
    DOMAIN_ENDPOINT=$(aws opensearch describe-domain \
        --domain-name $OPENSEARCH_DOMAIN_NAME \
        --region $REGION \
        --query 'DomainStatus.Endpoint' \
        --output text)
    
    # Test connection
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN_ENDPOINT")
    
    if [ "$RESPONSE" = "200" ]; then
        print_status "✅ OpenSearch connection successful"
        
        # Get cluster info
        curl -s "https://$DOMAIN_ENDPOINT" | python3 -m json.tool
        
        return 0
    else
        print_error "❌ OpenSearch connection failed (HTTP $RESPONSE)"
        return 1
    fi
}

# Function to configure OpenSearch for Python client
configure_opensearch_client() {
    print_status "Setting up OpenSearch Python client configuration..."
    
    # Get domain endpoint
    DOMAIN_ENDPOINT=$(aws opensearch describe-domain \
        --domain-name $OPENSEARCH_DOMAIN_NAME \
        --region $REGION \
        --query 'DomainStatus.Endpoint' \
        --output text)
    
    # Create Python configuration snippet
    cat > opensearch_config.py << EOF
"""
OpenSearch configuration for RAG Chatbot
Generated by AWS vector database setup script
"""
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# AWS Configuration
AWS_REGION = '$REGION'
OPENSEARCH_ENDPOINT = '$DOMAIN_ENDPOINT'
INDEX_NAME = 'rag-vectors'

def get_opensearch_client():
    """Get configured OpenSearch client with AWS authentication"""
    
    # Get AWS credentials
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        AWS_REGION,
        'es',
        session_token=credentials.token
    )
    
    # Create OpenSearch client
    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    return client

def test_connection():
    """Test OpenSearch connection"""
    try:
        client = get_opensearch_client()
        info = client.info()
        print(f"Connected to OpenSearch cluster: {info['cluster_name']}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
EOF
    
    print_status "OpenSearch client configuration saved to opensearch_config.py"
    
    # Test the configuration
    python3 opensearch_config.py
}

# Function to show OpenSearch status
show_opensearch_status() {
    print_status "OpenSearch Domain Status:"
    
    aws opensearch describe-domain \
        --domain-name $OPENSEARCH_DOMAIN_NAME \
        --region $REGION \
        --query 'DomainStatus.{
            Name: DomainName,
            Endpoint: Endpoint,
            Processing: Processing,
            Created: Created,
            Deleted: Deleted,
            InstanceType: ClusterConfig.InstanceType,
            InstanceCount: ClusterConfig.InstanceCount,
            VolumeSize: EBSOptions.VolumeSize
        }' \
        --output table
}

# Function to cleanup OpenSearch resources
cleanup_opensearch() {
    print_warning "This will delete the OpenSearch domain and all data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deleting OpenSearch domain..."
        
        aws cloudformation delete-stack \
            --stack-name $STACK_NAME \
            --region $REGION
        
        print_status "Deletion initiated. This may take several minutes..."
        
        # Clean up local files
        rm -f opensearch_config.py opensearch-template.yaml
        
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy      - Deploy OpenSearch domain"
    echo "  index       - Create vector index"
    echo "  test        - Test OpenSearch connection"
    echo "  configure   - Setup Python client configuration"
    echo "  status      - Show OpenSearch domain status"
    echo "  cleanup     - Delete OpenSearch domain"
    echo ""
    echo "Options:"
    echo "  --domain NAME     OpenSearch domain name (default: rag-chatbot-search)"
    echo "  --instance TYPE   Instance type (default: t3.small.search)"
    echo "  --region REGION   AWS region (default: us-east-1)"
    echo ""
    echo "Environment Variables:"
    echo "  AWS_REGION        AWS region"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 deploy --domain my-search --instance t3.medium.search"
    echo "  $0 test"
    echo "  $0 cleanup"
}

# Main execution
main() {
    print_header
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --domain)
                OPENSEARCH_DOMAIN_NAME="$2"
                shift 2
                ;;
            --instance)
                INSTANCE_TYPE="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            deploy)
                COMMAND="deploy"
                shift
                ;;
            index)
                COMMAND="index"
                shift
                ;;
            test)
                COMMAND="test"
                shift
                ;;
            configure)
                COMMAND="configure"
                shift
                ;;
            status)
                COMMAND="status"
                shift
                ;;
            cleanup)
                COMMAND="cleanup"
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                COMMAND="${1:-deploy}"
                shift
                ;;
        esac
    done
    
    # Set default command
    COMMAND="${COMMAND:-deploy}"
    
    echo "Region: $REGION"
    echo "Domain: $OPENSEARCH_DOMAIN_NAME"
    echo "Instance Type: $INSTANCE_TYPE"
    echo ""
    
    # Check AWS CLI for all commands except help
    check_aws_cli
    
    # Execute command
    case $COMMAND in
        deploy)
            deploy_opensearch
            ;;
        index)
            create_vector_index
            ;;
        test)
            test_opensearch
            ;;
        configure)
            configure_opensearch_client
            ;;
        status)
            show_opensearch_status
            ;;
        cleanup)
            cleanup_opensearch
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
    
    print_status "AWS vector database operation completed!"
}

# Run main function with all arguments
main "$@"
