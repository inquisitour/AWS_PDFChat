import boto3
import psycopg2
from psycopg2 import extras
import json
import os
from botocore.exceptions import ClientError

# Initialize the AWS S3 client
s3 = boto3.client('s3')

def clean_string(input_string):
    """Remove null bytes from the string"""
    return input_string.replace('\x00', '')

def lambda_handler(event, context):
    try:
        bucket = event['bucket']
        embedding_key = event['embedding_key']
        
        print(f"Processing embedding: {embedding_key}")
        
        # Database connection parameters from environment variables
        db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }
        
        # Retrieve the embedding data from S3
        try:
            embedding_data = s3.get_object(Bucket=bucket, Key=embedding_key)
            embedding_content = json.loads(embedding_data['Body'].read())
        except ClientError as e:
            print(f"Error retrieving embedding from S3: {e}")
            return {
                'statusCode': 404,
                'body': json.dumps('Embedding not found in S3')
            }
        
        # Clean the text to remove any null bytes
        cleaned_text = clean_string(embedding_content['text'])
        
        # Convert the embedding to a format suitable for PostgreSQL
        embedding = embedding_content['embedding']
        
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        try:
            # Ensure the pgvector extension is created and create table
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'pdf_chunks') THEN
                    CREATE TABLE pdf_chunks (
                        id SERIAL PRIMARY KEY,
                        pdf_id UUID NOT NULL,
                        chunk_index INT NOT NULL,
                        file_path TEXT,
                        content TEXT,
                        content_embedding VECTOR(1024),
                        client_id UUID,
                        is_pdf_chat BOOLEAN
                    );
                    CREATE INDEX IF NOT EXISTS pdf_chunks_embedding_idx ON pdf_chunks USING ivfflat (content_embedding vector_cosine_ops);
                END IF;
            END
            $$;
            """)
            conn.commit()
        
            # Prepare the data for batch insertion
            insert_data = [
                (
                    embedding_content['pdf_id'],
                    embedding_content['chunk_index'],
                    embedding_key,
                    cleaned_text,
                    embedding,
                    embedding_content.get('client_id'),
                    embedding_content.get('is_pdf_chat', False)
                )
            ]
        
            # Batch insert the embedding data into the database
            insert_query = """
            INSERT INTO pdf_chunks (pdf_id, chunk_index, file_path, content, content_embedding, client_id, is_pdf_chat)
            VALUES (%s, %s, %s, %s, %s::VECTOR, %s, %s)
            """
            extras.execute_batch(cur, insert_query, insert_data)
            conn.commit()
            print(f"Embedding stored successfully for PDF: {embedding_content['pdf_id']}")
        
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            # Close the database connection
            cur.close()
            conn.close()
        
        # Prepare the response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Embedding stored successfully.',
                'pdf_id': embedding_content['pdf_id'],
                'client_id': embedding_content.get('client_id'),
                'is_pdf_chat': embedding_content.get('is_pdf_chat', False)
            })
        }
        
        # Only include sessionAttributes if they exist in the event
        if 'sessionAttributes' in event:
            session_attributes = event['sessionAttributes']
            session_attributes['is_pdf_chat'] = embedding_content.get('is_pdf_chat', False)
            response['sessionAttributes'] = session_attributes
        
        return response

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error storing embedding: {str(e)}')
        }
