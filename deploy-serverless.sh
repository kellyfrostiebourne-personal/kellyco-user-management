#!/bin/bash

# Serverless Deployment Script for Kelly's User Management System
# Usage: ./deploy-serverless.sh [stage] [region]

set -e

# Configuration
STAGE=${1:-dev}
AWS_REGION=${2:-us-east-1}
SERVICE_NAME="kelly-user-management"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo_error "Serverless Framework is not installed. Please install it first:"
    echo "npm install -g serverless"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo_error "Node.js is not installed. Please install it first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo_error "AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

echo_info "Starting serverless deployment for ${STAGE} stage in ${AWS_REGION}"

# Install Serverless plugins if not already installed
echo_step "Installing Serverless plugins..."
if [ ! -d "node_modules" ]; then
    npm init -y
fi

npm install --save-dev serverless-python-requirements serverless-offline

# Deploy the serverless stack
echo_step "Deploying serverless infrastructure..."
serverless deploy --stage ${STAGE} --region ${AWS_REGION} --verbose

# Get deployment information
echo_step "Getting deployment information..."
API_URL=$(serverless info --stage ${STAGE} --region ${AWS_REGION} | grep "ServiceEndpoint:" | sed 's/ServiceEndpoint: //')
FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${SERVICE_NAME}-${STAGE}" \
    --region "${AWS_REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
    --output text 2>/dev/null || echo "")

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
    --stack-name "${SERVICE_NAME}-${STAGE}" \
    --region "${AWS_REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
    --output text 2>/dev/null || echo "")

echo_info "Backend API deployed successfully!"
echo_info "API URL: ${API_URL}"

# Deploy frontend if bucket exists
if [ ! -z "$FRONTEND_BUCKET" ]; then
    echo_step "Building and deploying frontend..."
    
    cd frontend
    
    # Install dependencies
    npm ci
    
    # Build React app with correct API URL
    REACT_APP_API_URL="${API_URL}" npm run build
    
    # Upload to S3
    aws s3 sync build/ "s3://${FRONTEND_BUCKET}/" --delete --region "${AWS_REGION}"
    
    # Invalidate CloudFront cache if distribution exists
    if [ ! -z "$CLOUDFRONT_URL" ]; then
        echo_step "Invalidating CloudFront cache..."
        DISTRIBUTION_ID=$(aws cloudfront list-distributions \
            --query "DistributionList.Items[?Origins.Items[0].DomainName=='${FRONTEND_BUCKET}.s3.amazonaws.com'].Id" \
            --output text)
        
        if [ ! -z "$DISTRIBUTION_ID" ]; then
            aws cloudfront create-invalidation \
                --distribution-id "$DISTRIBUTION_ID" \
                --paths "/*"
        fi
    fi
    
    cd ..
    
    echo_info "Frontend deployed successfully!"
    echo_info "Frontend URL: https://${CLOUDFRONT_URL}"
fi

echo_info "Deployment completed successfully!"
echo_info "🚀 Serverless API: ${API_URL}"
echo_info "🌐 Frontend: https://${CLOUDFRONT_URL}"
echo_info "🔍 Health Check: ${API_URL}/api/health"

echo_warn "Note: It may take a few minutes for CloudFront to propagate changes globally."

# Test the deployment
echo_step "Testing API deployment..."
sleep 5
HEALTH_RESPONSE=$(curl -s "${API_URL}/api/health" || echo "")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo_info "✅ API health check passed!"
else
    echo_warn "⚠️ API health check failed. The deployment may still be propagating."
fi
