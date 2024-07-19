import json
import boto3
import os
from botocore.exceptions import ClientError

sns_client = boto3.client('sns')
lex_client = boto3.client('lex-runtime')

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
BOT_NAME = os.environ['BOT_NAME']
BOT_ALIAS = os.environ['BOT_ALIAS']

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
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject='PDF Processing Failure Alert'
        )
        
        print(f"SNS notification sent: {json.dumps(sns_response)}")
        
        # Update Lex session to indicate processing failure
        try:
            lex_response = lex_client.post_text(
                botName=BOT_NAME,
                botAlias=BOT_ALIAS,
                userId=client_id,
                inputText='notify_pdf_processing_failed',
                sessionAttributes={
                    'pdf_id': pdf_id,
                    'client_id': client_id,
                    'processing_complete': 'false',
                    'processing_failed': 'true'
                }
            )
            print(f"Lex session updated: {json.dumps(lex_response)}")
        except ClientError as lex_error:
            print(f"Error updating Lex session: {lex_error}")
        
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