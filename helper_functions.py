from langchain.embeddings.openai import OpenAIEmbeddings
import os
import openai
import warnings

# Ignore all warnings
warnings.filterwarnings('ignore')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Initialize the embeddings
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-large", dimensions=1024)

def get_embedding(text: str) -> list:
    if not text or not isinstance(text, str):
        return None
    try:
        embedding_result = embeddings.embed_documents([text])
        return embedding_result[0]  # Return the first (and only) embedding
    except Exception as e:
        print(f"Error in generating embedding for text '{text}': {e}")
        return None

def find_most_relevant_content(query_embedding, cursor, table, pdf_id=None, limit=1):
    try:
        # Format the embedding as a PostgreSQL array
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        if pdf_id:
            sql_query = f"""
                SELECT content
                FROM {table}
                WHERE pdf_id = %s
                ORDER BY content_embedding <-> %s::vector
                LIMIT %s;
            """
            cursor.execute(sql_query, (pdf_id, embedding_str, limit))
        else:
            sql_query = f"""
                SELECT content
                FROM {table}
                ORDER BY content_embedding <-> %s::vector
                LIMIT %s;
            """
            cursor.execute(sql_query, (embedding_str, limit))
        
        result = cursor.fetchone()
        return result['content'] if result else None
    except Exception as e:
        print(f"Error in find_most_relevant_content: {e}")
        return None

def process_user_query(user_query, context, is_pdf_chat):
    try:
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
    except Exception as e:
        print(f"Error in process_user_query: {e}")
        return "I apologize, but I encountered an error while processing your query. Please try again later."

def create_response_card():
    buttons = [{"text": "Main Menu", "value": "main menu"}]
    return {
        "version": 1,
        "contentType": "application/vnd.amazonaws.card.generic",
        "genericAttachments": [{"buttons": buttons}]
    }
