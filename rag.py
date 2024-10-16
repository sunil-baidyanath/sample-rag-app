'''
Created on Oct 15, 2024

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

from store import BlobStorageStore

class RAGEngine(object):
    
    def __init__(self):

        basedir = os.path.abspath(os.path.dirname(__file__))
        
                
        # Load configurations
        with open(os.path.join(basedir, 'settings.json')) as fp:
            self.config = json.load(fp)
            
        print(self.config.keys())
                
        # Load api keys        
        load_dotenv()
        llm_api_key = os.getenv("LLM_API_KEY")
        embedding_api_key = os.getenv('EMBEDDING_MODEL_API_KEY')
        
        storage_access_key = self.config['knowledgebase']['access_key']
        
        self.document_store = BlobStorageStore('documents', storage_access_key)
        self.index_store = BlobStorageStore('indexes', storage_access_key)
        
             
        # Configure llm
        llm=AzureOpenAI(
            deployment_name=self.config['llm']['deployment_name'],
            model=self.config['llm']["model"], 
            api_key=llm_api_key,
            azure_endpoint=self.config['llm']['azure_endpoint'],
            api_version=self.config['llm']['api_version'], 
            temperature=self.config['llm']['temperature'],
            max_tokens=256)
                
        # Configure embedding model
        embed_model = AzureOpenAIEmbedding(
            azure_deployment=self.config['embedding']['deployment_name'],
            model=self.config['embedding']["model"], 
            api_key=embedding_api_key,
            azure_endpoint=self.config['embedding']['azure_endpoint'],
            api_version=self.config['embedding']['api_version'],
            chunk_size=1)
                
        # Configure chunking
        text_splitter=SentenceSplitter(chunk_size=1024, chunk_overlap=20)
                
        # Setup Settings used by the RAG functions
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.text_splitter = text_splitter
        Settings.context_window = 4096
        Settings.num_output = 256

    # Load or build knowledge base
    def load_or_build_index(self, index_name):
        index_root_path = self.config['knowledgebase']['location']
        configured_indexes = {}
        
        for item in self.config["knowledgebase"]["indexes"]:
            configured_indexes[item['name']] = item
            
        print(configured_indexes)
        print(index_name)
            
        if index_name in configured_indexes.keys():
            item = configured_indexes[index_name]
            if self.index_store.exists_file(join(index_root_path, item["name"], 'index_store.json')):
                self.index_store.download_files(join(index_root_path, item["name"]))
                                                 
                # Load index
                storage_context = StorageContext.from_defaults(persist_dir=item["name"])
                index = load_index_from_storage(storage_context)
            else:
                #Build index
                self.document_store.download_files(item["data_source"]["location"])
                        
                documents = SimpleDirectoryReader(input_files=[os.path.basename(item["data_source"]["location"])]).load_data()
                index = VectorStoreIndex.from_documents(documents)
                index.set_index_id(item["name"])
                            
                # Persist index to disk, default "storage" folder
                index.storage_context.persist(persist_dir=join(index_root_path, item["name"]))
                    
            return index
        else:
            raise f"Invalid index {index_name}!"
            
    def configure(self, index_name):
            
        index = self.load_or_build_index(index_name)
               
        # Build RAG engine    
        self.engine = index.as_chat_engine(chat_mode="condense_plus_context",
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
        
        
    # Create the chat function for the chatbot app    
    def stream_chat(self, query: str, history: list[ChatMessage]) -> Iterable[str]:
        messages = [ChatMessage(role="user", content=message.content) for message in history]
        messages.append(ChatMessage(role="user", content=query))
            
        response = self.engine.stream_chat(query, chat_history=messages)
        for text in response.response_gen:
            yield text
    
    
