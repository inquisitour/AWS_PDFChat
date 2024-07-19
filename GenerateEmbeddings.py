import boto3
import os
import openai
import json
from botocore.exceptions import ClientError
import time

# Set the OpenAI API key using environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the AWS S3 client
s3 = boto3.client('s3')

def get_embedding(text: str, max_retries=3) -> list:
    for attempt in range(max_retries):
        try:
            # Obtain the embedding using the updated OpenAI API approach
            response = openai.Embedding.create(
                input=text, 
                model="text-embedding-3-large",
                dimensions=1024
            )
            return response['data'][0]['embedding']
        except openai.error.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

def lambda_handler(event, context):
    try:
        bucket = event['bucket']
        chunk_key = event['chunk_key']
        embeddings_dir = event['embeddings_dir']
        
        print(f"Processing chunk: {chunk_key}")
        
        # Retrieve the chunk data from S3
        try:
            chunk_data = s3.get_object(Bucket=bucket, Key=chunk_key)
            chunk_content = json.loads(chunk_data['Body'].read())
        except ClientError as e:
            print(f"Error retrieving chunk from S3: {e}")
            return {
                'statusCode': 404,
                'body': json.dumps('Chunk not found in S3')
            }
        
        text = chunk_content['text']
        embedding = get_embedding(text)
        
        # Define the key for storing the embedding in S3
        embedding_key = f"{embeddings_dir}{os.path.basename(chunk_key).replace('chunk_', 'embedding_')}"
        
        # Store the embedding in S3
        embedding_data = {
            'text': text,
            'embedding': embedding,
            'pdf_id': chunk_content['pdf_id'],
            'chunk_index': chunk_content['chunk_index'],
            'client_id': chunk_content.get('client_id'),
            'is_pdf_chat': chunk_content.get('is_pdf_chat', False)
        }
        
        s3.put_object(Bucket=bucket, Key=embedding_key, Body=json.dumps(embedding_data))
        
        print(f"Embedding generated and stored: {embedding_key}")
        
        return {
            'statusCode': 200,
            'embedding_key': embedding_key,
            'bucket': bucket,
            'pdf_id': chunk_content['pdf_id'],
            'client_id': chunk_content.get('client_id'),
            'is_pdf_chat': chunk_content.get('is_pdf_chat', False)
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error generating embedding: {str(e)}')
        }
