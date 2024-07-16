import boto3
import os
import openai
import json

# Set the OpenAI API key using environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the AWS S3 client
s3 = boto3.client('s3')

def get_embedding(text: str) -> list:
    # Obtain the embedding using the updated OpenAI API approach
    response = openai.Embedding.create(
        input=text, 
        model="text-embedding-3-large",
        dimensions=1024
    )
    return response['data'][0]['embedding']

def lambda_handler(event, context):
    bucket = event['bucket']
    chunk_key = event['chunk_key']
    embeddings_dir = event['embeddings_dir']
    
    # Retrieve the chunk data from S3
    chunk_data = s3.get_object(Bucket=bucket, Key=chunk_key)
    chunk_content = json.loads(chunk_data['Body'].read())
    
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
    
    return {
        'statusCode': 200,
        'embedding_key': embedding_key,
        'bucket': bucket,
        'pdf_id': chunk_content['pdf_id'],
        'client_id': chunk_content.get('client_id'),
        'is_pdf_chat': chunk_content.get('is_pdf_chat', False)
    }