'''
Created on Jun 11, 2024

@author: sunilthakur
'''

# def setup():
#     # setup orchestrator
#
# def process_user_query():
#     # convert user query to embedding
#
# def load_data():
#     #perform semantic search
#
# def build_prompt():
#     # build prompt for llm
#
# def get_llm_response():
#     # get response from llm
#
# def process_llm_response():
#     # process response from llm
#
#
# def run_query(profile = None):
# # 1.    Setup chatbot profile if it’s first query from the user for this conversation thread
# # 2.    Process user query by using appropriate embedding model
# # 3.    Retrieve relevant text from knowledgebase using semantic search
# # 4.    Extract conversation context from past chat history
# # 5.    Prepare chain/prompt for LLM
# # 6.    Receive response from LLM
# # 7.    Prepare the response for end user
#
#     if not profile:
#         profile = setup()
#
#
#
#

# https://dev.to/alvinslee/how-to-implement-rag-with-llamaindex-langchain-and-heroku-a-simple-walkthrough-29ij
# https://medium.com/@prasadmahamulkar/introduction-to-retrieval-augmented-generation-rag-using-langchain-and-lamaindex-bd0047628e2a

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os

if os.environ.get('OPENAI_API_KEY') is None:
  exit('You must provide an OPENAI_API_KEY env var.')

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("In which city is Saint Augustine the Bishop?")
print(response)

PERSIST_DIR='./my_vector_indexes/gutenberg/'
index.storage_context.persist(persist_dir=PERSIST_DIR)

import os
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langchain_community.retrievers import LlamaIndexRetriever

from fastapi import FastAPI
from pydantic import BaseModel


from llama_index.core import (
    SimpleDirectoryReader,
    # LLMPredictor,
    PromptHelper,
    ServiceContext,
    StorageContext,
    # LangchainEmbedding,
    GPTVectorStoreIndex,
    load_index_from_storage,
    set_global_service_context)

# from llama_index.llm_predictor import LLMPredictor
# from llama_index.embeddings.langchain import LangchainEmbedding

from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.node_parser.text.token import TokenTextSplitter


if os.environ.get('OPENAI_API_KEY') is None:
  exit('You must provide an OPENAI_API_KEY env var.')

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

# For this demo, we will not persist the index.


retriever = LlamaIndexRetriever(index=index.as_query_engine())

llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=2048)

memory = ConversationBufferWindowMemory(
  memory_key='chat_history',
  return_messages=True,
  k=3
)

conversation = ConversationalRetrievalChain.from_llm(
  llm=llm, 
  retriever=retriever,
  memory=memory,
  max_tokens_limit=1536  
)

class Prompt(BaseModel):
  question: str

app = FastAPI()

@app.post("/prompt")
async def query_chatbot(prompt: Prompt):
  response = conversation.invoke({'question': prompt.question})
  return response['answer']

if __name__=='__main__':
  import uvicorn
  uvicorn.run(app, host="localhost", port=8000)
  
  
  
# Use Llamaindex for indexing and retrieval pipelines while langchain is used for building the chatbot

