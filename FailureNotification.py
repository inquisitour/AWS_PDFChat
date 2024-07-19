import json
import boto3
import os
from botocore.exceptions import ClientError

sns_client = boto3.client('sns')
TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    pdf_id = event['pdf_id']
    client_id = event['client_id']
    error = event['error']
    
    message = f"""
    PDF Processing Failure Notification:
    PDF ID: {pdf_id}
    Client ID: {client_id}
    Error: {error}
    """
    
    try:
        # Send SNS notification
        sns_response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
            Subject='PDF Processing Failure Alert'
        )
        
        print(f"SNS notification sent: {json.dumps(sns_response)}")
        
        # You could also add code here to update a database or the Lex bot session
        # to indicate that an error occurred during processing
        
        return {
            'statusCode': 200,
            'body': json.dumps('Failure notification sent successfully')
        }
    
    except ClientError as e:
        print(f"Error sending SNS notification: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error sending failure notification: {str(e)}')
        }
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Unexpected error: {str(e)}')
        }