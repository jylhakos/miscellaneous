# AWS serverless deployment

## Overview

This document walks you through deploying the LangChain.js text transformation application to AWS Lambda with API Gateway. 

The deployment creates a RESTful API that can transform text to uppercase using LangChain.js in a serverless environment.

## Architecture

```
Internet → API Gateway → Lambda Function → LangChain.js → Response
```

### Amazon AWS components

- **AWS Lambda**: Serverless compute service running the Node.js application
- **API Gateway**: RESTful API endpoint that routes requests to Lambda
- **IAM Role**: Security role with necessary permissions
- **CloudWatch**: Logging and monitoring
- **X-Ray**: Distributed tracing (optional)

## Prerequisites

1. **AWS Account**: Active AWS account with CLI access
2. **Node.js**: Version 14 or higher
3. **Linux/Debian**: Terminal access for script execution

## Setup

### 1. Install dependencies

```bash
# Install Node.js dependencies
npm install

# Install serverless dependencies
npm install -g serverless
```

### 2. Configure AWS credentials

```bash
# Install AWS CLI (automated by setup script)
./scripts/setup-aws.sh

# Configure AWS credentials manually (if needed)
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., us-east-1)
- Output format (json)

### 3. Set up IAM permissions

The setup script automatically creates:
- **IAM Role**: `LangChainServerlessRole`
- **IAM Policy**: `LangChainServerlessPolicy`

Manual setup (if needed):
```bash
# Create IAM policy
aws iam create-policy \
  --policy-name LangChainServerlessPolicy \
  --policy-document file://aws/iam-policy.json

# Create IAM role
aws iam create-role \
  --role-name LangChainServerlessRole \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":["lambda.amazonaws.com","apigateway.amazonaws.com"]},"Action":"sts:AssumeRole"}]}'

# Attach policy to role
aws iam attach-role-policy \
  --role-name LangChainServerlessRole \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/LangChainServerlessPolicy
```

## Deployment

### Development

```bash
# Deploy to development stage
npm run deploy

# Or manually specify stage and region
./scripts/deploy.sh dev us-east-1
```

### Production

```bash
# Deploy to production stage
npm run deploy:prod

# Or manually
./scripts/deploy.sh prod us-east-1
```

### Local testing

```bash
# Start local development server
npm run test:local

# Test locally at http://localhost:3000
curl -X POST http://localhost:3000/transform \
  -H 'Content-Type: application/json' \
  -d '{"text": "hello world"}'
```

## API Endpoints

### POST /transform
Transform text to uppercase using LangChain.js

**Request:**
```json
{
  "text": "hello langchain"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "originalText": "hello langchain",
    "transformedText": "HELLO LANGCHAIN",
    "processingTimeMs": 45,
    "timestamp": "2025-01-15T10:30:00.000Z"
  },
  "meta": {
    "requestId": "abc123-def456",
    "functionName": "langchain-text-transformer-dev-transformText"
  }
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "LangChain service is operational",
  "test": {
    "input": "health check",
    "output": "HEALTH CHECK"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

## Testing

### Automated testing

```bash
# Test deployed API
npm run test:api https://your-api-id.execute-api.us-east-1.amazonaws.com/dev

# View logs
npm run logs

# Run unit tests
npm test
```

### Manual testing

```bash
# Health check
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/health

# Text transformation
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/transform \
  -H 'Content-Type: application/json' \
  -d '{"text": "hello serverless langchain"}'
```

## Monitoring and debugging

### CloudWatch logs

```bash
# View real-time logs
aws logs tail /aws/lambda/langchain-text-transformer-dev-transformText --follow

# View specific log group
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/langchain"
```

### X-Ray tracing

Access AWS X-Ray console to view:
- Request traces
- Performance metrics
- Error analysis
- Service map

### Metrics

Key metrics to monitor:
- **Duration**: Function execution time
- **Errors**: Error rate and types
- **Throttles**: Rate limiting events
- **Invocations**: Total request count

## Configuration

### Environment variables

Edit `serverless.yml` to add environment variables:
```yaml
provider:
  environment:
    NODE_ENV: ${self:provider.stage}
    LOG_LEVEL: info
    CUSTOM_VAR: value
```

### Memory and timeout

Adjust in `serverless.yml`:
```yaml
provider:
  memorySize: 512  # MB
  timeout: 30      # seconds
```

### CORS configuration

CORS is configured in `serverless.yml`:
```yaml
cors:
  origin: '*'
  headers:
    - Content-Type
    - Authorization
```

## Security

### IAM permissions

The deployment uses least-privilege IAM policies:
- Lambda execution permissions
- CloudWatch logging
- X-Ray tracing
- API Gateway integration

### API security

Consider adding:
- API Keys
- JWT authentication
- Rate limiting
- Input validation

Example API key setup:
```yaml
functions:
  transformText:
    events:
      - http:
          path: /transform
          method: post
          private: true  # Requires API key
```

## Cost optimization

### Lambda pricing

- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second
- **Free Tier**: 1M requests and 400,000 GB-seconds/month

### Optimization

1. **Right-size memory**: Start with 512MB, adjust based on usage
2. **Minimize cold starts**: Keep functions warm with scheduled invocations
3. **Optimize bundle size**: Exclude dev dependencies from deployment
4. **Use provisioned concurrency**: For consistent performance (paid feature)

## Troubleshooting

### Issues

1. **Deployment fails**: Check AWS credentials and permissions
2. **Function timeout**: Increase timeout in serverless.yml
3. **Memory limit**: Increase memorySize in serverless.yml
4. **CORS errors**: Verify CORS configuration in serverless.yml

### Debug

```bash
# Check serverless configuration
serverless print

# Validate CloudFormation template
aws cloudformation validate-template --template-body file://.serverless/cloudformation-template-update-stack.json

# Test function locally
serverless invoke local -f transformText -d '{"httpMethod":"POST","body":"{\"text\":\"test\"}"}'
```

## Cleanup

### Remove deployment

```bash
# Remove all AWS resources
npm run remove

# Or manually
serverless remove --stage dev
```

This will delete:
- Lambda functions
- API Gateway
- CloudWatch log groups
- IAM roles (if created by Serverless)

### Manual cleanup

```bash
# Delete IAM policy
aws iam delete-policy --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/LangChainServerlessPolicy

# Delete IAM role
aws iam delete-role --role-name LangChainServerlessRole
```