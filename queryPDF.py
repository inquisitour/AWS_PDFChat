import json
import boto3
import os
import psycopg2
from psycopg2.extras import DictCursor
from helper_functions import get_embedding, find_most_relevant_content, process_user_query, create_response_card

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    # Extract session attributes and user query
    session_attributes = event.get('sessionAttributes', {})
    user_query = event['inputTranscript']
    #user_query = "what is this pdf about?"
    
    is_pdf_chat = session_attributes.get('is_pdf_chat') == 'true'
    processing_complete = session_attributes.get('processing_complete') == 'true'
    pdf_id = session_attributes.get('pdf_id')
    
    print(f"Session attributes: {json.dumps(session_attributes)}")
    print(f"is_pdf_chat: {is_pdf_chat}, processing_complete: {processing_complete}, pdf_id: {pdf_id}")
    
    if is_pdf_chat and not processing_complete:
        return {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'Your PDF is still being processed. Please wait a moment before asking questions.'
                }
            }
        }
    
    try:
        # Get embedding for user query
        query_embedding = get_embedding(user_query)
        if query_embedding is None:
            raise ValueError("Failed to generate embedding for user query")
        
        # Connect to the PostgreSQL database
        db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }
        print(f"Attempting to connect to database: {db_params['dbname']} on host: {db_params['host']}")
        
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                if is_pdf_chat:
                    closest_content = find_most_relevant_content(query_embedding, cur, "pdf_chunks", pdf_id)
                else:
                    closest_content = find_most_relevant_content(query_embedding, cur, "pdf_chunks")
        
        if closest_content is None:
            print("No relevant content found in the database")
            closest_content = ""
        
        answer = process_user_query(user_query, closest_content, is_pdf_chat)
        
        return {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {
                    'contentType': 'PlainText',
                    'content': answer
                }
            }
        }
    
    except Exception as e:
        print(f"Error in QueryPDF Lambda: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Failed',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'I apologize, but I encountered an error while processing your query. Please try again later.'
                }
            }
        }
