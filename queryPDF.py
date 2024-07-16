import logging
import os
import json
import psycopg2
import openai
from psycopg2.extras import DictCursor

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import helper functions
from helper_functions import get_embedding, find_most_relevant_content, create_response_card

def process_user_query(user_query, context, is_pdf_chat):
    prompt = f"""
    You are an intelligent PDF assistant. Your primary function is to help users extract relevant information from PDF documents based on their queries. Follow these steps meticulously:

    1. Analyze the user's query, correcting any spelling errors and clarifying ambiguous terms using advanced natural language processing techniques.
    2. Conduct a semantic search within the provided PDF content to identify the most relevant information that addresses the preprocessed user query.
    3. Utilize the given context (most relevant PDF content) to formulate a comprehensive, accurate, and detailed response.
    4. If the provided context lacks relevant information to answer the query, respond with: "I apologize, but I couldn't find relevant information in the current PDF to answer your question. Could you please rephrase your query or ask about a different topic from the document?"

    Present your response to the user in a maximum of 4 concise yet informative bullet points. Use the "~" symbol at the end of each bullet point, except for the last one:

    "• Bullet Point 1~
     • Bullet Point 2~
     • Bullet Point 3~
     • Bullet Point 4"

    Remember, you are {'specifically addressing the content of a particular PDF' if is_pdf_chat else 'searching across multiple PDF documents'}. Tailor your response accordingly.

    User Query: {user_query}
    Context: {context}
    Answer:
    """

    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].text.strip()

def dispatch(intent_request):
    logger.debug("Intent Request: %s", json.dumps(intent_request))
    session_attributes = intent_request.get('sessionAttributes', {})
    slots = intent_request['currentIntent']['slots']
    user_query = slots['UserQuery']
    
    # Get embedding for user query
    query_embedding = get_embedding(user_query)
    response_card = create_response_card()
    
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    
    closest_content = None
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # Check if we're in a PDF chat session
            is_pdf_chat = session_attributes.get('is_pdf_chat', False)
            if is_pdf_chat:
                # If in PDF chat, use the client_id to filter results
                client_id = session_attributes.get('client_id')
                closest_content = find_most_relevant_content(query_embedding, cur, "pdf_chunks", client_id)
            else:
                # If not in PDF chat, use the general search
                closest_content = find_most_relevant_content(query_embedding, cur, "pdf_chunks")
    finally:
        conn.close()
    
    # Prepare the context for the prompt
    context = closest_content if closest_content else ""
    
    # Generate the final answer using the context
    answer = process_user_query(user_query, context)
    
    # Prepare Lex response
    response = {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': answer  # Send back the generated answer
            },
            #'responseCard': response_card
        },
        'sessionAttributes': session_attributes  # Include session attributes in the response
    }
    return response

def lambda_handler(event, context):
    try:
        response = dispatch(event)
        return response
    except Exception as e:
        logger.error(f"Error processing the request: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }