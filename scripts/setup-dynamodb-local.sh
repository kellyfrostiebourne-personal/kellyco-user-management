#!/bin/bash

# Setup script for local DynamoDB development
# Creates the users table in DynamoDB Local

set -e

DYNAMODB_ENDPOINT="http://localhost:8000"
TABLE_NAME="kelly-user-management-dev-users"
REGION="us-east-1"

echo "Setting up DynamoDB Local table: $TABLE_NAME"

# Wait for DynamoDB Local to be ready
echo "Waiting for DynamoDB Local to start..."
while ! curl -s $DYNAMODB_ENDPOINT > /dev/null; do
    echo "Waiting for DynamoDB Local..."
    sleep 2
done

echo "DynamoDB Local is ready!"

# Create the users table
echo "Creating users table..."
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=username,AttributeType=S \
        AttributeName=email,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        'IndexName=username-index,KeySchema=[{AttributeName=username,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
        'IndexName=email-index,KeySchema=[{AttributeName=email,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url $DYNAMODB_ENDPOINT \
    --region $REGION

echo "✅ DynamoDB Local setup complete!"
echo "Table: $TABLE_NAME"
echo "Endpoint: $DYNAMODB_ENDPOINT"
echo "Admin UI: http://localhost:8001"
