#!/bin/bash

# IAM setup script for RAG Chatbot deployment
# This script helps create the necessary IAM users, roles, and policies for deployment

set -e

# Configuration
POLICY_NAME="RAGChatbotDeploymentPolicy"
USER_NAME="rag-chatbot-deployer"
ROLE_NAME="RAGChatbotCloudFormationRole"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI not configured. Please run 'aws configure' first."
        exit 1
    fi
}

# Function to create IAM policy
create_iam_policy() {
    print_status "Creating IAM policy: ${POLICY_NAME}..."
    
    # Check if policy already exists
    if aws iam get-policy --policy-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/${POLICY_NAME}" &> /dev/null; then
        print_warning "Policy ${POLICY_NAME} already exists. Updating..."
        
        # Create new policy version
        aws iam create-policy-version \
            --policy-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/${POLICY_NAME}" \
            --policy-document file://aws/iam-deployment-policy.json \
            --set-as-default
    else
        # Create new policy
        aws iam create-policy \
            --policy-name ${POLICY_NAME} \
            --policy-document file://aws/iam-deployment-policy.json \
            --description "Policy for RAG Chatbot deployment on AWS"
    fi
    
    print_status "Policy created/updated successfully."
}

# Function to create IAM user for deployment
create_iam_user() {
    print_status "Creating IAM user: ${USER_NAME}..."
    
    # Check if user already exists
    if aws iam get-user --user-name ${USER_NAME} &> /dev/null; then
        print_warning "User ${USER_NAME} already exists."
    else
        # Create user
        aws iam create-user \
            --user-name ${USER_NAME} \
            --path "/rag-chatbot/"
        
        print_status "User created successfully."
    fi
    
    # Attach policy to user
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    aws iam attach-user-policy \
        --user-name ${USER_NAME} \
        --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}"
    
    print_status "Policy attached to user."
}

# Function to create access keys
create_access_keys() {
    print_status "Creating access keys for user: ${USER_NAME}..."
    
    # Delete existing access keys if any
    local existing_keys=$(aws iam list-access-keys --user-name ${USER_NAME} --query 'AccessKeyMetadata[].AccessKeyId' --output text)
    
    for key in $existing_keys; do
        print_warning "Deleting existing access key: ${key}"
        aws iam delete-access-key --user-name ${USER_NAME} --access-key-id ${key}
    done
    
    # Create new access key
    local access_key_output=$(aws iam create-access-key --user-name ${USER_NAME} --output json)
    
    local access_key_id=$(echo ${access_key_output} | jq -r '.AccessKey.AccessKeyId')
    local secret_access_key=$(echo ${access_key_output} | jq -r '.AccessKey.SecretAccessKey')
    
    echo ""
    print_status "Access keys created successfully!"
    echo ""
    echo "=== IMPORTANT: Save these credentials securely ==="
    echo "AWS_ACCESS_KEY_ID=${access_key_id}"
    echo "AWS_SECRET_ACCESS_KEY=${secret_access_key}"
    echo "=================================================="
    echo ""
    echo "Add these to your .env file or configure with:"
    echo "aws configure --profile rag-chatbot"
}

# Function to create CloudFormation service role
create_cloudformation_role() {
    print_status "Creating CloudFormation service role: ${ROLE_NAME}..."
    
    # Trust policy for CloudFormation
    local trust_policy='{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudformation.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'
    
    # Check if role already exists
    if aws iam get-role --role-name ${ROLE_NAME} &> /dev/null; then
        print_warning "Role ${ROLE_NAME} already exists."
    else
        # Create role
        aws iam create-role \
            --role-name ${ROLE_NAME} \
            --assume-role-policy-document "${trust_policy}" \
            --description "CloudFormation service role for RAG Chatbot"
        
        print_status "Role created successfully."
    fi
    
    # Attach policy to role
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    aws iam attach-role-policy \
        --role-name ${ROLE_NAME} \
        --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}"
    
    print_status "Policy attached to CloudFormation role."
}

# Function to validate permissions
validate_permissions() {
    print_status "Validating permissions..."
    
    # Test basic AWS operations
    aws sts get-caller-identity > /dev/null
    aws ec2 describe-regions --region us-east-1 > /dev/null
    aws s3 ls > /dev/null
    
    print_status "Basic permissions validated successfully."
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [setup-user|setup-role|validate|cleanup]"
    echo ""
    echo "Commands:"
    echo "  setup-user  - Create IAM user with deployment permissions"
    echo "  setup-role  - Create CloudFormation service role"
    echo "  validate    - Validate current permissions"
    echo "  cleanup     - Remove created IAM resources"
    echo ""
    echo "Example:"
    echo "  $0 setup-user"
}

# Function to cleanup IAM resources
cleanup() {
    print_warning "Cleaning up IAM resources..."
    
    # Detach and delete user policies
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    
    if aws iam get-user --user-name ${USER_NAME} &> /dev/null; then
        aws iam detach-user-policy \
            --user-name ${USER_NAME} \
            --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}" || true
        
        # Delete access keys
        local access_keys=$(aws iam list-access-keys --user-name ${USER_NAME} --query 'AccessKeyMetadata[].AccessKeyId' --output text)
        for key in $access_keys; do
            aws iam delete-access-key --user-name ${USER_NAME} --access-key-id ${key}
        done
        
        # Delete user
        aws iam delete-user --user-name ${USER_NAME}
        print_status "User ${USER_NAME} deleted."
    fi
    
    # Delete role
    if aws iam get-role --role-name ${ROLE_NAME} &> /dev/null; then
        aws iam detach-role-policy \
            --role-name ${ROLE_NAME} \
            --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}" || true
        
        aws iam delete-role --role-name ${ROLE_NAME}
        print_status "Role ${ROLE_NAME} deleted."
    fi
    
    # Delete policy
    if aws iam get-policy --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}" &> /dev/null; then
        # Delete all policy versions except default
        local versions=$(aws iam list-policy-versions --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}" --query 'Versions[?!IsDefaultVersion].VersionId' --output text)
        for version in $versions; do
            aws iam delete-policy-version \
                --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}" \
                --version-id ${version}
        done
        
        aws iam delete-policy --policy-arn "arn:aws:iam::${account_id}:policy/${POLICY_NAME}"
        print_status "Policy ${POLICY_NAME} deleted."
    fi
    
    print_status "Cleanup completed."
}

# Main execution
main() {
    case "${1:-setup-user}" in
        setup-user)
            check_aws_cli
            create_iam_policy
            create_iam_user
            create_access_keys
            ;;
        setup-role)
            check_aws_cli
            create_iam_policy
            create_cloudformation_role
            ;;
        validate)
            check_aws_cli
            validate_permissions
            ;;
        cleanup)
            check_aws_cli
            cleanup
            ;;
        help|-h|--help)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
