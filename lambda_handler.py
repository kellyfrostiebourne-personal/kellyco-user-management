#!/usr/bin/env python3
"""
AWS Lambda handler for Kelly's User Management System
Serverless Flask application handler
"""

import json
import os
from serverless_wsgi import handle_request
from web_app import create_app

# Create Flask app instance
app = create_app()

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
        
    Returns:
        dict: HTTP response for API Gateway
    """
    try:
        # Handle the request using serverless-wsgi
        return handle_request(app, event, context)
    except Exception as e:
        # Log error and return 500 response
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

# For local testing
if __name__ == "__main__":
    # Run Flask app locally
    app.run(debug=True, host='0.0.0.0', port=8080)
