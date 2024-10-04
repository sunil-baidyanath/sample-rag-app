'''
Created on Jul 31, 2024

@author: sunilthakur
'''
import json
from os import listdir
from os.path import isfile, join, exists

from llama_index.core import (
    SimpleDirectoryReader,
    ServiceContext,
    VectorStoreIndex,
)

from llama_index.core.node_parser.text import SentenceSplitter
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

def configure_context():
    '''
    '''
    
    llm = AzureOpenAI(
        deployment_name="gpt-functions",
        model="gpt-3.5-turbo", 
        api_key="fb569c7a7f444edc82d434e58b525dd7",
        azure_endpoint="https://arogya-kys-ai.openai.azure.com/",
        api_version="2023-12-01-preview", temperature=0.0)
    

    embed_model = AzureOpenAIEmbedding(
        model="text-embedding-ada-002",
        deployment_name="text-embedding",
        api_key="fb569c7a7f444edc82d434e58b525dd7",
        azure_endpoint="https://arogya-kys-ai.openai.azure.com/",
        api_version="2023-07-01-preview")
    
    text_splitter=SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    
    
    service_context = ServiceContext.from_defaults(
        llm = llm,
        embed_model=embed_model,
        text_splitter = text_splitter,
        context_window=4096,
        num_output = 256
    )
    
    return service_context
    
    
def build_index(index_name: str, sourcepath: str, index_location: str):
    
    # Loads data from the specified directory path
    
    service_context = configure_context()
        
    documents = SimpleDirectoryReader(input_files=[sourcepath]).load_data()
        
    # When first building the index
    index = VectorStoreIndex.from_documents(
        documents, service_context=service_context
    )
    
    index.set_index_id(index_name)
        
    # Persist index to disk, default "storage" folder
    index.storage_context.persist(persist_dir=index_location)
        
    print(f"Saved the indexes at {index_location}")
    

def list_indexes(index_location=None):
    index_location = '/Users/sunilthakur/indexes'
        
    indexes = [f for f in listdir(index_location) if not isfile(join(index_location, f))]
    
    items = []    
    for index in indexes:
        if exists(join(index_location, index, 'index_store.json')):
            with open(join(index_location, index, 'index_store.json')) as f:
                items.extend([{'index_name': item, 'index_location': join(index_location, index)} for item in list(json.load(f)['index_store/data'].keys())])
        
    return items
    
def main():
    # index_name = 'activity'
    # sourcepath = '/Users/sunilthakur/Downloads/Physical_Activity_Guidelines_2nd_edition.pdf'
    # index_location = '/Users/sunilthakur/activities'
    
    index_name = 'diet'
    sourcepath = '/Users/sunilthakur/Downloads/Dietary_Guidelines_for_Americans-2020-2025.pdf'
    index_location = '/Users/sunilthakur/diets'
    
    # build_index(index_name, sourcepath, index_location)
    
    list_indexes()
    
if __name__ == '__main__':
    main()