"""
Amazon SageMaker deployment script for Llama3 model
This script helps deploy a Llama3 model to Amazon SageMaker JumpStart
"""
import boto3
import sagemaker
from sagemaker.jumpstart.model import JumpStartModel
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
import json
import time

# Configuration
MODEL_ID = "meta-textgeneration-llama-3-8b-instruct"  # Llama3 8B Instruct model
INSTANCE_TYPE = "ml.g5.xlarge"  # Instance type for deployment
ENDPOINT_NAME = "llama3-rag-endpoint"

def deploy_llama3_model():
    """Deploy Llama3 model to SageMaker"""
    try:
        # Initialize SageMaker session
        sagemaker_session = sagemaker.Session()
        role = sagemaker.get_execution_role()
        
        print(f"Using role: {role}")
        print(f"Deploying model: {MODEL_ID}")
        
        # Create JumpStart model
        model = JumpStartModel(
            model_id=MODEL_ID,
            role=role,
            sagemaker_session=sagemaker_session
        )
        
        # Deploy the model
        print(f"Deploying to endpoint: {ENDPOINT_NAME}")
        print("This may take 10-15 minutes...")
        
        predictor = model.deploy(
            endpoint_name=ENDPOINT_NAME,
            instance_type=INSTANCE_TYPE,
            initial_instance_count=1,
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer()
        )
        
        print(f"Model deployed successfully to endpoint: {ENDPOINT_NAME}")
        
        # Test the endpoint
        test_endpoint(predictor)
        
        return predictor
        
    except Exception as e:
        print(f"Error deploying model: {e}")
        raise

def test_endpoint(predictor):
    """Test the deployed endpoint"""
    try:
        print("Testing the endpoint...")
        
        # Test payload
        test_payload = {
            "inputs": "What is machine learning?",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        # Make prediction
        response = predictor.predict(test_payload)
        print(f"Test response: {response}")
        
    except Exception as e:
        print(f"Error testing endpoint: {e}")

def create_sagemaker_role():
    """Create IAM role for SageMaker if needed"""
    iam = boto3.client('iam')
    
    role_name = 'SageMakerRAGChatbotRole'
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "sagemaker.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Try to get existing role
        role = iam.get_role(RoleName=role_name)
        print(f"Using existing role: {role['Role']['Arn']}")
        return role['Role']['Arn']
        
    except iam.exceptions.NoSuchEntityException:
        # Create new role
        print(f"Creating new role: {role_name}")
        
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for RAG Chatbot SageMaker operations'
        )
        
        # Attach necessary policies
        policies = [
            'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'
        ]
        
        for policy in policies:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy
            )
        
        print(f"Created role: {role['Role']['Arn']}")
        return role['Role']['Arn']

def cleanup_endpoint(endpoint_name: str = ENDPOINT_NAME):
    """Clean up SageMaker endpoint to avoid charges"""
    try:
        sagemaker_client = boto3.client('sagemaker')
        
        print(f"Deleting endpoint: {endpoint_name}")
        sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        
        print(f"Deleting endpoint configuration: {endpoint_name}")
        sagemaker_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        
        print("Cleanup completed")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SageMaker deployment for RAG Chatbot")
    parser.add_argument(
        'action',
        choices=['deploy', 'test', 'cleanup'],
        help='Action to perform'
    )
    parser.add_argument(
        '--endpoint-name',
        default=ENDPOINT_NAME,
        help='SageMaker endpoint name'
    )
    
    args = parser.parse_args()
    
    if args.action == 'deploy':
        deploy_llama3_model()
    elif args.action == 'test':
        # Test existing endpoint
        sagemaker_runtime = boto3.client('sagemaker-runtime')
        test_payload = {
            "inputs": "What is machine learning?",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7
            }
        }
        
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=args.endpoint_name,
            ContentType='application/json',
            Body=json.dumps(test_payload)
        )
        
        result = json.loads(response['Body'].read().decode())
        print(f"Response: {result}")
        
    elif args.action == 'cleanup':
        cleanup_endpoint(args.endpoint_name)
