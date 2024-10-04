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

class IndexEngine(object):
    
    def __init__(self, config, setting=None):
        self.document_store_location = config['document_store']['source']['location']
        self.index_store_location = config['index_store']['source']['location']
    
    def build_index(self, index_name: str, sourcepath: str): 
        # Loads data from the specified directory path
        documents_path = join(self.document_store_location, sourcepath)         
        documents = SimpleDirectoryReader(documents_path).load_data()
            
        # When first building the index
        index = VectorStoreIndex.from_documents(documents)
        index.set_index_id(index_name)
            
        # Persist index to disk, default "storage" folder
        index_path = join(self.index_store_location, index_name)
        index.storage_context.persist(persist_dir=index_path)
            
        print(f"Saved the index {index_name} at {index_path}")
    

    def list_indexes(self):   
        # List all directories from a given index store location 
        indexes = [f for f in listdir(self.index_store_location) if not isfile(join(self.index_store_location, f))]
        
        # Check if the directory has index_store_store.json file
        # And if so, read the file to get the name of the index
        items = []    
        for index in indexes:
            if exists(join(self.index_store_location, index, 'index_store.json')):
                with open(join(self.index_store_location, index, 'index_store.json')) as f:
                    items.extend([{'index_name': item, 'index_location': join(self.index_store_location, index)} for item in list(json.load(f)['index_store/data'].keys())])
            
        return items

        

class RAGEngine(object):
    
    def __init__(self, config, setting=None):
        self.setting = setting
        self.engine = self.configure()
        self.indexes = list_indexes()
        

    def configure(self, index_name: str = None, persona: str = None, context: str = None):
        # state = me.state(State)
        
        index_location = "/Users/sunilthakur/indexes/diets"
        
        storage_context = StorageContext.from_defaults(persist_dir=index_location)
        
        # storage_context = StorageContext.from_defaults(persist_dir=index_location, index_id=index_name)
        
        index = load_index_from_storage(storage_context)
        
        memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
    
        engine = index.as_chat_engine(chat_mode="condense_plus_context",
            similarity_top_k=1,
            memory=memory,
            system_prompt = ( 
                "I am a nutritional and dietary consultant named Mycroft who helps people find best nutritional and dietary guidelines"
                "based on the document provided."
                "I am professional and friendly. I introduce myself first before answering any query."
                "When helping people out, I always ask them for this information to inform the dietary recommendation I provide:"
                "1.    What is their age?"
                "2.    What is their gender?"
                "I will then provide the appropriate diet plan and guidelines and answer any queries with regards to their nutritional and dietary concerns"
                ),
            context_template=(
                "You are a helpful chatbot, able to have interactions as well as talk about nutrition and dietary guidelines."
                "Here are the relevant documents for the context:\n"
                "{context_str}"
                "Given the context information and not prior knowledge, answer the query"
                # "\nInstruction: Use only the previous chat history, or the context above, to interact and help the user."
                # "Make sure to provide answers based solely on the information from the document provided and the chat history"
                # "If the information isn't available in the given document to formulate the answer, just say that you don't know."
            ),
            verbose = False
        
        )
    
        return engine
    
    
    def stream_chat(self, query: str, history: list[ChatMessage]) -> Iterable[str]:
        messages = [ChatMessage(role="system", content="You are a helpful assistant able to hold a warm and professional conversation.")]
        messages.extend([ChatMessage(role="user", content=message.content) for message in history])
        messages.append(ChatMessage(role="user", content=query))
        
        query = "\n".join([
            query, 
            "Use only the document and the chat history to answer the query", 
            "If the document and the chat history do not contain any relevant information, please say so. Don't answer from any other source."
        ])
        
        response = self.engine.stream_chat(query, chat_history=messages)
        for text in response.response_gen:
            yield text


class RAGSettings(object):
    
    def __init__(self, **kwargs):
        self.llm = None
        self.embed_model = None
        self.text_splitter = None
    
        for key, value in kwargs.items():
            if 'llm' == key:
                self.llm = value
            if 'embed_model' == key:
                self.embed_model = value
            if 'text_splitter' == value:
                self.text_splitter = value
                
        
    @classmethod
    def configure(cls, config=None, cred=None):
        basedir = os.path.abspath(os.path.dirname(__file__))
        
        # Load configurations
        if not config:
            with open(os.path.join(basedir, 'settings.json')) as fp:
                config = json.load(fp)
        
        # Load api keys        
        if not cred:
            load_dotenv()
            llm_api_key = os.getenv("LLM_API_KEY")
            embedding_api_key = os.getenv('EMBEDDING_MODEL_API_KEY')
            
        else:
            llm_api_key = cred['LLM_API_KEY']
            embedding_api_key = cred['EMBEDDING_MODEL_API_KEY']
            
        
        # Configure llm
        llm=AzureOpenAI(
              #temperature=0.5,
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
        
        return RAGSettings(llm=llm, embed_model=embed_model, text_splitter=text_splitter)
        