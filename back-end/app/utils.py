import ast
import ollama
from tqdm import tqdm
from colorama import Fore
from .chat_agent import client, convo
from .database import connect_db
import chromadb

def create_queries(prompt):
    query_msg = (
        'You are a first principle reasoning search query AI agent. '
        'Your list of search queries will be run on an embedding database of all your conversations '
        'you have ever had with the user. With first principles create a Python list of queries to '
        'search the embeddings database for any data that would be necessary to have access to in '
        'order to correctly respond to the prompt. Your response must be a Python list with no syntax errors. '
        'Do not explain anything and do not ever generate anything but a perfect syntax Python list.'
    )
    query_convo = [
        {'role': 'system', 'content': query_msg},
        {'role': 'user', 'content': 'Write an email to my car insurance company and create a persuasive request for them to lower my rate.'},
        {'role': 'assistant', 'content': '["What is the user\'s name?", "What is the user\'s current auto insurance provider?", "What the monthly rate the user currently pays for auto insurance?"]'},
        {'role': 'user', 'content': 'how can i convert the speak function in my llama3 python voice assistant to use pyttsx3 instead of openai TTS?'},
        {'role': 'assistant', 'content': '["llama3 voice assistant", "Python voice assistant", "OpenAI TTS", "openai speak", "pyttsx3"]'},
        {'role': 'user', 'content': prompt}
    ]   
    response = ollama.chat(model='llama3.1', messages=query_convo)
    print(Fore.YELLOW + f"\nVector Database Queries: {response['message']['content']}\n")
    try:
        return ast.literal_eval(response['message']['content'])
    except:
        return [prompt]

def classify_embeddings(query, context):
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You will not respond as an AI assistant. You only respond "yes" or "no". '
        'Determine whether the context contains data that directly is related to the search query. '
        'If the context is seemingly exactly what the search query needs, respond "yes" and if it is anything but directly '
        'related respond "no". Do NOT respond "yes" unless the content is highly relevant to the search query.'
    )
    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': 'SEARCH QUERY: What is the user\'s name? \n\nEMBEDDED CONTEXT: You are AI Austin. How can I help you today?'},
        {'role': 'assistant', 'content': 'yes'},
        {'role': 'user', 'content': 'SEARCH QUERY: Llama3 Python Voice Assistant \n\nEMBEDDED CONTEXT: Siri is a voice assistant developed by Apple.'},
        {'role': 'assistant', 'content': 'no'},
        {'role': 'user', 'content': f'SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context}'}
    ]
    response = ollama.chat(model='llama3.1', messages=classify_convo)
    return response['message']['content'].strip().lower()

def retrieve_embedding(queries, result_per_query=2):
    embeddings = set()
    for query in tqdm(queries, desc='Processing Queries to Vector Database'):
        response = ollama.embeddings(model='nomic-embed-text', prompt=query)
        query_embedding = response['embedding']
        vector_db = client.get_collection(name='conversations')
        result = vector_db.query(query_embeddings=[query_embedding], n_results=result_per_query)
        best_embeddings = result['documents'][0]
        for best in best_embeddings:
            if best not in embeddings:
                if 'yes' in classify_embeddings(query=query, context=best):
                    embeddings.add(best)
    print(Fore.LIGHTMAGENTA_EX + f"\n Final Embeddings: {embeddings}")
    return embeddings

def recall(prompt):
    queries = create_queries(prompt=prompt)
    embeddings = retrieve_embedding(queries=queries)
    convo.append({'role': 'user', 'content': f'MEMORIES: {embeddings} \n\n USER PROMPT: {prompt}'})
    print(f'\n{len(embeddings)} message response embeddings added for context.')
