from llama_index.core import (
    SimpleDirectoryReader,
    PromptHelper,
    ServiceContext,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    set_global_service_context)

from llama_index.core.storage.index_store.simple_index_store import SimpleIndexStore
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore
from llama_index.core.vector_stores.simple import SimpleVectorStore
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.node_parser.text.token import TokenTextSplitter
from llama_index.core.node_parser.text import SentenceSplitter
from llama_index.embeddings.langchain import LangchainEmbedding

# from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
# from llama_index.llms.langchain import LangChainLLM
# from langchain.embeddings.azure_openai import AzureOpenAIEmbeddings

class Pipeline(object):
    
    def __init__(self):
        '''
        '''
  

class IndexPipeline(Pipeline):
    def __init__(self, config):
        self.config = config
        self.soure_location = config['data_store']['source']['location']
        self.source_type = config['data_store']['source']['type']
        
        
    def run(self):
        '''
        load_data
        split_data
        generate_embeddings
        
        '''
        self.service_context=PipelineContext(self.config).get_service_context()
        Settings.llm = self.service_context.llm
        Settings.embed_model = self.service_context.embed_model
        Settings.text_splitter = self.service_context.text_splitter
        Settings.context_window = 4096
        Settings.num_output = 256
        # Loads data from the specified directory path
        
        documents = SimpleDirectoryReader(input_files=[self.soure_location]).load_data()
        
        # When first building the index
        # index = VectorStoreIndex.from_documents(
        #     documents, service_context=PipelineContext(self.config).get_service_context()
        #     )
        index = VectorStoreIndex.from_documents(documents)
        
        # Persist index to disk, default "storage" folder
        index.storage_context.persist(persist_dir=self.config['index_store']['source']['location'])
        
        print(f"Saved the indexes at {self.config['index_store']['source']['location']}")
        
        # return index
        
        
class QueryPipeline(Pipeline):
    
    def __init__(self, config):
        '''
        Initialize the storage context for index
        '''
        
        self.config = config
        self.persist_dir = config['index_store']['source']['location']
        # self.index_id = config['index_id']
        self.storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
                # docstore=SimpleDocumentStore.from_persist_dir(persist_dir=self.persist_dir),
                # vector_store=SimpleVectorStore.from_persist_dir(persist_dir=self.persist_dir)
                # index_store=SimpleIndexStore.from_persist_dir(persist_dir=self.persist_dir),
        # )
        self.service_context=PipelineContext(self.config).get_service_context()
        
    def run(self, query):
        '''
        load_index
        create_engine
        query_engine
        '''
        Settings.llm = self.service_context.llm
        Settings.embed_model = self.service_context.embed_model
        
        index = load_index_from_storage(self.storage_context)
        
        # , index_id=self.index_id
        query_engine = index.as_query_engine()
        result = query_engine.query(query)
        
        return result

class PipelineContext(object):
    
    def __init__(self, config):
        self.config = config
    
    def get_service_context(self):
        # Constraint parameters
        
        max_input_size = 4096,        # Context window for the LLM.
        num_outputs = 256,            # Number of output tokens for the LLM.
        chunk_overlap_ratio = 0.1,    # Chunk overlap as a ratio of chunk size.
        chunk_size_limit = None,      # Maximum chunk size to use.
        chunk_overlap = 20,           # Chunk overlap to use.
        chunk_size = 1024,            # Set chunk overlap to use.
        
    
        # The parser that converts documents into nodes.
        # node_parser = SimpleNodeParser.from_defaults(
        #     # The text splitter used to split text into chunks.
        #     # text_splitter=TokenTextSplitter(chunk_size=1024, chunk_overlap=20)
        #     text_splitter=SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        #   )
        text_splitter=SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    
        # Allows the user to explicitly set certain constraint parameters.
        # prompt_helper = PromptHelper(
        #     max_input_size,
        #     num_outputs,
        #     chunk_overlap_ratio,
        #     chunk_size_limit=chunk_size_limit)
    
        # # LLMPredictor is a wrapper class around LangChain's LLMChain that allows easy integration into LlamaIndex.
        # llm_predictor = LLMPredictor(
        llm=AzureOpenAI(
              #temperature=0.5,
              deployment_name=self.config['llm']['deployment_name'],
              model=self.config['llm']["model"], 
              api_key=self.config['llm']['api_key'],
              azure_endpoint=self.config['llm']['azure_endpoint'],
              api_version=self.config['llm']['api_version'], temperature=self.config['llm']['temperature'],
              max_tokens=256)
            
    
        ## The embedding model used to generate vector representations of text.
        embed_model = AzureOpenAIEmbedding(
              azure_deployment=self.config['embedding']['deployment_name'],
              model=self.config['embedding']["model"], 
              api_key=self.config['embedding']['api_key'],
              azure_endpoint=self.config['embedding']['azure_endpoint'],
              api_version=self.config['embedding']['api_version'],
              chunk_size=1)
          
    
        # Constructs service context
        service_context = ServiceContext.from_defaults(
            # llm_predictor=llm_predictor,
            llm = llm,
            embed_model=embed_model,
            text_splitter = text_splitter,
            context_window=4096,
            num_output = 256
            # node_parser=node_parser,
            # prompt_helper=prompt_helper
            )
    
        return service_context
        
    