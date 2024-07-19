import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize clients
lex_client = boto3.client('lex-runtime')
sns_client = boto3.client('sns')

# Environment variables
BOT_NAME = os.environ['BOT_NAME']
BOT_ALIAS = os.environ['BOT_ALIAS']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    pdf_id = event['pdf_id']
    client_id = event['client_id']
    is_pdf_chat = event['is_pdf_chat']
    processing_complete = event['processing_complete']
    
    try:
        # Update Lex session attributes
        session_attributes = {
            'pdf_id': pdf_id,
            'client_id': client_id,
            'is_pdf_chat': str(is_pdf_chat).lower(),
            'processing_complete': str(processing_complete).lower()
        }

        lex_response = lex_client.post_text(
            botName=BOT_NAME,
            botAlias=BOT_ALIAS,
            userId=client_id,
            inputText='update_pdf_processing_status',
            sessionAttributes=session_attributes
        )
        
        print(f"Lex response: {json.dumps(lex_response)}")
        
        # Notify user that PDF processing is complete if processing_complete is True
        if processing_complete:
            completion_message = "PDF processing is complete"
            send_message_to_user(client_id, session_attributes, completion_message)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Lex session updated successfully'),
            'sessionAttributes': lex_response['sessionAttributes']
        }
    
    except Exception as e:
        error_message = f"Error updating Lex session for PDF ID {pdf_id}, Client ID {client_id}: {str(e)}"
        print(error_message)
        
        try:
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps({
                    'pdf_id': pdf_id,
                    'client_id': client_id,
                    'error': error_message
                }),
                Subject='Lex Session Update Failure'
            )
        except Exception as sns_error:
            print(f"Error sending SNS notification: {sns_error}")
        
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }

def send_message_to_user(client_id, session_attributes, message):
    try:
        # Use post_text to send a message and maintain the session
        lex_response = lex_client.post_text(
            botName=BOT_NAME,
            botAlias=BOT_ALIAS,
            userId=client_id,
            inputText=message,  # Send the message as input text
            sessionAttributes=session_attributes
        )
        print(f"Notification sent to user {client_id}: {json.dumps(lex_response)}")
    except ClientError as e:
        print(f"Error sending message to user {client_id}: {e}")
