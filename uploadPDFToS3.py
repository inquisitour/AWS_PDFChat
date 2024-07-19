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
        print("Event:", event)
        body = json.loads(event['body'])
        print("Parsed Body:", body)

        client_id = body['client_id']
        is_pdf_chat = body.get('is_pdf_chat', False)
        pdf_id = body.get('pdf_id') or str(uuid.uuid4())
        file_content = base64.b64decode(body['file'])
        file_name = f"{client_id}_{pdf_id}.pdf"

        unique_dir = f"{FOLDER_NAME}{pdf_id}/"
        chunks_dir = f"{unique_dir}chunks/"
        embeddings_dir = f"{unique_dir}embeddings/"
        
        s3_object_path = f"{unique_dir}{file_name}"
        
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_object_path, Body=file_content)
        
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
        
        try:
            lex_response = lex_client.post_text(
                botName=BOT_NAME,
                botAlias=BOT_ALIAS,
                userId=client_id,
                inputText='notify_pdf_processing_started',
                sessionAttributes={
                    'pdf_id': pdf_id,
                    'client_id': client_id,
                    'is_pdf_chat': str(is_pdf_chat).lower(),
                    'processing_complete': 'false'
                }
            )
            print("Lex Response:", lex_response)
        except ClientError as lex_error:
            print("Lex ClientError:", lex_error)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'message': 'File uploaded successfully and processing started.',
                'executionArn': stepfunctions_response['executionArn'],
                'pdf_id': pdf_id
            })
        }
    except ClientError as e:
        print("ClientError:", e)
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
        print("Exception:", e)
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