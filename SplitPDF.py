import json
import fitz  # PyMuPDF
import re
import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket = event['bucket']
        key = event['key']
        chunks_dir = event['chunks_dir']
        pdf_id = event['pdf_id']
        client_id = event.get('client_id')
        is_pdf_chat = event.get('is_pdf_chat', False)
        
        chunk_size = event.get('chunk_size', 750)
        chunk_overlap = event.get('chunk_overlap', 300)
        
        print(f"Processing PDF: {pdf_id} for client: {client_id}")
        
        # Download the file from S3
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            pdf_content = response['Body'].read()
        except ClientError as e:
            print(f"Error downloading PDF from S3: {e}")
            return {
                'statusCode': 404,
                'body': json.dumps('PDF file not found in S3')
            }
        
        # Open the PDF content from memory
        document = fitz.open(stream=pdf_content, filetype="pdf")
        
        text_chunks = []
        current_chunk = ""
        chunk_keys = []
        
        def add_chunk(chunk, index):
            chunk_key = f'{chunks_dir}chunk_{index}.json'
            chunk_data = {
                'text': chunk.strip(),
                'chunk_key': chunk_key,
                'chunk_index': index,
                'pdf_id': pdf_id,
                'client_id': client_id,
                'is_pdf_chat': is_pdf_chat
            }
            s3.put_object(Bucket=bucket, Key=chunk_key, Body=json.dumps(chunk_data))
            chunk_keys.append(chunk_key)
            print(f"Chunk {index} created: {chunk_key}")
        
        bullet_point_pattern = re.compile(r'^(\d+[\.\)]|\*|•|-)\s')
        sentence_pattern = re.compile(r'(?<=[.!?]) +')
        
        for page_index, page in enumerate(document):
            text = page.get_text()
            lines = text.splitlines()
            for line in lines:
                if bullet_point_pattern.match(line.strip()):
                    if len(current_chunk) + len(line) <= chunk_size:
                        current_chunk += line + "\n"
                    else:
                        add_chunk(current_chunk, len(chunk_keys))
                        current_chunk = line + "\n"
                else:
                    sentences = sentence_pattern.split(line)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= chunk_size:
                            current_chunk += sentence + " "
                        else:
                            add_chunk(current_chunk, len(chunk_keys))
                            current_chunk = sentence + " "
        
        if current_chunk.strip():
            add_chunk(current_chunk, len(chunk_keys))
        
        print(f"PDF processing complete. Total chunks: {len(chunk_keys)}")
        
        return {
            'statusCode': 200,
            'chunk_keys': chunk_keys,
            'bucket': bucket,
            'pdf_id': pdf_id,
            'client_id': client_id,
            'is_pdf_chat': is_pdf_chat
        }
    except fitz.FitzError as fe:
        print(f"FitzError while processing PDF: {fe}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error processing PDF file: {fe}')
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal server error: {e}')
        }
