'''
Created on Jul 20, 2024

@author: sunilthakur
'''
import os
import json
from os import listdir
from os.path import isfile, join, exists
from typing import Iterable
from dotenv import load_dotenv

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import (
    Settings, 
    StorageContext, 
    load_index_from_storage
)

from llama_index.core.memory import ChatMemoryBuffer

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
)

from llama_index.core.node_parser.text import SentenceSplitter
from llama_index.core.llms import ChatMessage

from app.knowledgebase import list_indexes

basedir = os.path.abspath(os.path.dirname(__file__))
        
# Load configurations
with open(os.path.join(basedir, 'settings.json')) as fp:
    config = json.load(fp)
        
# Load api keys        
load_dotenv()
llm_api_key = os.getenv("LLM_API_KEY")
embedding_api_key = os.getenv('EMBEDDING_MODEL_API_KEY')
     
# Configure llm
llm=AzureOpenAI(
    deployment_name=config['llm']['deployment_name'],
    model=config['llm']["model"], 
    api_key=llm_api_key,
    azure_endpoint=config['llm']['azure_endpoint'],
    api_version=config['llm']['api_version'], 
    temperature=config['llm']['temperature'],
    max_tokens=256)
        
# Configure embedding model
embed_model = AzureOpenAIEmbedding(
    azure_deployment=config['embedding']['deployment_name'],
    model=config['embedding']["model"], 
    api_key=embedding_api_key,
    azure_endpoint=config['embedding']['azure_endpoint'],
    api_version=config['embedding']['api_version'],
    chunk_size=1)
        
# Configure chunking
text_splitter=SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        
# Setup Settings used by the RAG functions
Settings.llm = llm
Settings.embed_model = embed_model
Settings.text_splitter = text_splitter
Settings.context_window = 4096
Settings.num_output = 256

# Build Indexes
document_store_location = config['document_store']['source']['location']
index_store_location = config['index_store']['source']['location']
    
# Loads data from the specified directory path
documents_path = join(self.document_store_location, sourcepath)         
documents = SimpleDirectoryReader(documents_path).load_data()
            
# Build the index
index = VectorStoreIndex.from_documents(documents)
index.set_index_id(index_name)
            
# Persist index to disk, default "storage" folder
index_path = join(self.index_store_location, index_name)
index.storage_context.persist(persist_dir=index_path)
            
print(f"Saved the index {index_name} at {index_path}")
    
# Build RAG Engine    
engine = index.as_chat_engine(chat_mode="condense_plus_context",
    similarity_top_k=1,
    system_prompt = ( 
                "I am a nutritional and dietary consultant named Mycroft who helps people find best nutritional and dietary guidelines"
                "based on the document provided."
                "I am professional and friendly able to hold a warm conversation."
                "When helping people out, I always ask them for this information to inform the dietary recommendation I provide:"
                "1.    What is their age?"
                "2.    What is their gender?"
                "I will then provide the appropriate diet plan and guidelines and answer any queries with regards to their nutritional and dietary concerns"
                ),
    context_template=(
                "Here are the relevant documents for the context:\n"
                "{context_str}"
                "Given the context information and not prior knowledge, answer the query"
            ),
            verbose = False
        )
        return engine

# Create the chat function for the chatbot app    
def stream_chat(query: str, history: list[ChatMessage]) -> Iterable[str]:
    messages.extend([ChatMessage(role="user", content=message.content) for message in history])
    messages.append(ChatMessage(role="user", content=query))
    
    response = self.engine.stream_chat(query, chat_history=messages)
    for text in response.response_gen:
        yield text
