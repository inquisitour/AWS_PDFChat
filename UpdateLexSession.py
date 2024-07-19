import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize clients
sns_client = boto3.client('sns')
lex_client = boto3.client('lex-runtime')

# Environment variables
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    if 'botName' in event and 'botAlias' in event and 'userId' in event:
        # Parameters passed from Step Functions
        bot_name = event['botName']
        bot_alias = event['botAlias']
        user_id = event['userId']
        input_text = event['inputText']
        session_attributes = event['sessionAttributes']
        
        # Convert boolean session attributes to strings
        for key, value in session_attributes.items():
            if isinstance(value, bool):
                session_attributes[key] = str(value).lower()
        
        try:
            response = lex_client.post_text(
                botName=bot_name,
                botAlias=bot_alias,
                userId=user_id,
                inputText=input_text,
                sessionAttributes=session_attributes
            )
            return response
        except ClientError as e:
            print(f"Error posting text to Lex: {e}")
            raise e

    # Extract information from the Lex event (for original use case)
    intent_name = event.get('currentIntent', {}).get('name', '')
    session_attributes = event.get('sessionAttributes', {})
    
    if intent_name != 'Notify_PDFChat':
        return {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Failed',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'This lambda function is designed to handle the Notify_PDFChat intent only.'
                }
            }
        }
    
    # Extract required information from session attributes
    pdf_id = session_attributes.get('pdf_id')
    client_id = session_attributes.get('client_id')
    is_pdf_chat = session_attributes.get('is_pdf_chat', 'false').lower() == 'true'
    processing_complete = session_attributes.get('processing_complete', 'false').lower() == 'true'
    
    try:
        # Update session attributes
        session_attributes['pdf_id'] = pdf_id
        session_attributes['client_id'] = client_id
        session_attributes['is_pdf_chat'] = str(is_pdf_chat).lower()
        session_attributes['processing_complete'] = str(processing_complete).lower()
        
        # Notify user that PDF processing is complete if processing_complete is True
        if processing_complete:
            completion_message = "PDF processing is complete. You can now ask questions about the document."
        else:
            completion_message = "PDF processing is still in progress. Please wait before asking questions."
        
        return {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {
                    'contentType': 'PlainText',
                    'content': completion_message
                }
            }
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
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Failed',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'An error occurred while processing your request. Please try again later.'
                }
            }
        }
