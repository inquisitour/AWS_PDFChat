import json
import base64
import boto3
import uuid
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
stepfunctions_client = boto3.client('stepfunctions')
lex_client = boto3.client('lex-runtime')

BUCKET_NAME = 'isckrs-conference-rawdata2'
FOLDER_NAME = 'PDF_Upload/'
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:510343462926:stateMachine:PDFChat_Agent'
BOT_NAME = 'PDFChatAgent'
BOT_ALIAS = 'pdfchatagent'

def lambda_handler(event, context):
    try:
        print("Event:", event)  # Log the event for debugging
        # Parse the body of the request
        body = json.loads(event['body'])
        print("Parsed Body:", body)  # Log the parsed body for debugging

        # Extract information from the new body format
        client_id = body['client_id']
        is_pdf_chat = body.get('is_pdf_chat', False)
        pdf_id = body.get('pdf_id') or str(uuid.uuid4())
        file_content = base64.b64decode(body['file'])
        file_name = f"{client_id}_{pdf_id}.pdf"

        # Create a unique directory for the file
        unique_dir = f"{FOLDER_NAME}{pdf_id}/"
        chunks_dir = f"{unique_dir}chunks/"
        embeddings_dir = f"{unique_dir}embeddings/"
        
        # Construct the full S3 object path with the folder
        s3_object_path = f"{unique_dir}{file_name}"
        
        # Upload the file to S3
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_object_path, Body=file_content)
        
        # Start the state machine execution
        stepfunctions_response = stepfunctions_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({
                'bucket': BUCKET_NAME,
                'key': s3_object_path,
                'chunks_dir': chunks_dir,
                'embeddings_dir': embeddings_dir,
                'pdf_id': pdf_id,
                'is_pdf_chat': is_pdf_chat,
                'client_id': client_id
            })
        )
        
        lex_message = "PDF processing started."  # Default message
        
        # Interact with Lex bot to set initial session attributes
        try:
            lex_response = lex_client.post_text(
                botName=BOT_NAME,
                botAlias=BOT_ALIAS,
                userId=client_id,
                inputText='start_pdf_processing',
                sessionAttributes={
                    'pdf_id': pdf_id,
                    'client_id': client_id,
                    'is_pdf_chat': str(is_pdf_chat).lower(),
                    'processing_complete': 'false'
                }
            )
            print("Lex Response:", lex_response)  # Log Lex response for debugging
            lex_message = lex_response.get('message', lex_message)  # Get the message from Lex response
        except ClientError as lex_error:
            print("Lex ClientError:", lex_error)  # Log Lex ClientError for debugging
            # Continue with the response even if Lex interaction fails
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'message': 'File uploaded successfully and state machine started.',
                'executionArn': stepfunctions_response['executionArn'],
                'pdf_id': pdf_id,
                'lex_message': lex_message
            })
        }
    except ClientError as e:
        print("ClientError:", e)  # Log ClientError for debugging
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(f'Error uploading file: {e}')
        }
    except Exception as e:
        print("Exception:", e)  # Log Exception for debugging
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(f'Invalid input: {e}')
        }