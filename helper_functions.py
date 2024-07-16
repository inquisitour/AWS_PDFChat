from langchain.embeddings.openai import OpenAIEmbeddings
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the embeddings
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-large", dimensions=1024)

def get_embedding(text: str) -> list:
    if not text or not isinstance(text, str):
        return None
    try:
        embedding_result = embeddings.embed_text(text)
        return embedding_result
    except Exception as e:
        print(f"Error in generating embedding for text '{text}': {e}")
        return None

def find_most_relevant_content(query_embedding, cursor, table, client_id=None, limit=1):
    if client_id:
        sql_query = f"""
            SELECT content
            FROM {table}
            WHERE client_id = %s
            ORDER BY content_embedding <-> %s::VECTOR
            LIMIT %s;
        """
        cursor.execute(sql_query, (client_id, query_embedding, limit))
    else:
        sql_query = f"""
            SELECT content
            FROM {table}
            ORDER BY content_embedding <-> %s::VECTOR
            LIMIT %s;
        """
        cursor.execute(sql_query, (query_embedding, limit))
    
    result = cursor.fetchone()
    return result['content'] if result else None

def create_response_card():
    buttons = [{"text": "Main Menu", "value": "main menu"}]
    return {
        "version": 1,
        "contentType": "application/vnd.amazonaws.card.generic",
        "genericAttachments": [{"buttons": buttons}]
    }