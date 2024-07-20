import json
import boto3
import os
from botocore.exceptions import ClientError

# Initialize the SNS client
sns_client = boto3.client('sns')
TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Check if the event is from SNS or direct invocation
        if 'Records' in event and 'Sns' in event['Records'][0]:
            # Extract the SNS message
            sns_message = event['Records'][0]['Sns']['Message']
            message_data = json.loads(sns_message)
        else:
            # Direct invocation from Step Functions
            message_data = event
        
        pdf_id = message_data.get('pdf_id', 'Unknown')
        client_id = message_data.get('client_id', 'Unknown')
        error = message_data.get('error', 'Unknown error')
        is_pdf_chat = str(message_data.get('is_pdf_chat', False)).lower()
        
        # The error is already formatted in the state machine, so we can use it directly
        error_message = error
        
        message = f"""
        PDF Processing Failure Notification:
        PDF ID: {pdf_id}
        Client ID: {client_id}
        Error: {error_message}
        Is PDF Chat: {is_pdf_chat}
        """
        
        # Send SNS notification
        sns_response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
            Subject='PDF Processing Failure Alert'
        )
        
        print(f"SNS notification sent: {json.dumps(sns_response)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Failure notification sent successfully')
        }
    
    except KeyError as e:
        error_message = f"Error accessing event data: {str(e)}"
        print(error_message)
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error processing event: {error_message}')
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