import os
import ast
import ollama
import chromadb
from colorama import Fore
from psycopg.rows import dict_row
from tqdm import tqdm
from .database import (
    fetch_conversations,
    store_conversations,
    remove_last_conversation,
    connect_db
)
from dotenv import load_dotenv

load_dotenv()

client = chromadb.Client()
system_prompt = (
    'You are an AI assistant that has memory of every conversation you have ever had with this user. '
    'On every prompt from the user, the system has checked for any relevant messages you have had with the user. '
    'If any embedded previous conversations are attached, use them for context to responding to the user, '
    'if the context is relevant and useful to responding. If the context is irrelevant, '
    'disregard speaking about them and respond normally as an AI assistant. Do not talk about recalling conversations. '
    'Just use any useful data from the previous conversations and respond normally as an intelligent AI assistant.'
)

convo = [{'role': 'system', 'content': system_prompt}]

def create_vector_db(conversations):
    vector_db_name = 'conversations'

    try:
        client.delete_collection(name=vector_db_name)
    except ValueError:
        pass

    vector_db = client.create_collection(name=vector_db_name)

    for convo_item in conversations:
        serialized_convo = f"prompt: {convo_item['prompt']} response: {convo_item['response']}"
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']

        vector_db.add(
            ids=[str(convo_item['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )

def update_vector_db():
    conn = connect_db()
    vector_db = client.get_collection(name='conversations')
    with conn.cursor(row_factory=dict_row) as cursor:
        chroma_ids = vector_db.get()['ids']
        max_id = max(int(id) for id in chroma_ids) if chroma_ids else 0
        cursor.execute('SELECT * FROM conversations WHERE id > %s ORDER BY id', (max_id,))
        new_conversations = cursor.fetchall()
    
    conn.close()
    for convo_item in new_conversations:
        serialized_convo = f"prompt: {convo_item['prompt']} response: {convo_item['response']}"
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']
        vector_db.add(
            ids=[str(convo_item['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )
    print(Fore.LIGHTMAGENTA_EX + f"\nAdded {len(new_conversations)} new conversations to the vector database.")

def stream_response(prompt, llm_api_key=None):
    response = ''
    # Initialize Ollama with user's API key if provided
    ollama_config = {'api_key': llm_api_key} if llm_api_key else {}
    stream = ollama.chat(model='llama3.1', messages=convo, stream=True, **ollama_config)
    print(Fore.LIGHTGREEN_EX + f"\nAssistant: ", end='')
    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)
    print('\n')
    store_conversations(prompt=prompt, response=response)
    convo.append({'role': 'assistant', 'content': response})

# Implement other functions like create_queries, retrieve_embedding, classify_embeddings, recall, etc.
# For brevity, they are omitted but should be integrated similarly.
