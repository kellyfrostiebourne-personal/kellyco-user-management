#!/bin/bash

# Setup script for todos DynamoDB table
# Creates the todos table in DynamoDB Local

set -e

DYNAMODB_ENDPOINT="http://localhost:8000"
TABLE_NAME="kelly-user-management-dev-todos"
REGION="us-east-1"

echo "Setting up DynamoDB Local todos table: $TABLE_NAME"

# Wait for DynamoDB Local to be ready
echo "Waiting for DynamoDB Local to start..."
while ! curl -s $DYNAMODB_ENDPOINT > /dev/null; do
    echo "Waiting for DynamoDB Local..."
    sleep 2
done

echo "DynamoDB Local is ready!"

# Create the todos table
echo "Creating todos table..."
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        'IndexName=user-id-index,KeySchema=[{AttributeName=user_id,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url $DYNAMODB_ENDPOINT \
    --region $REGION

echo "✅ DynamoDB todos table setup complete!"
echo "Table: $TABLE_NAME"
echo "Endpoint: $DYNAMODB_ENDPOINT"
