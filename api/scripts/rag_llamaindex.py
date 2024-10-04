'''
Created on Feb 16, 2024

@author: sunilthakur
'''
import tiktoken
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.indices import VectorStoreIndex 
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core import Settings

token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
)

llm = AzureOpenAI(
    deployment_name="gpt-functions",
    model="gpt-3.5-turbo", 
    api_key="fb569c7a7f444edc82d434e58b525dd7",
    azure_endpoint="https://arogya-kys-ai.openai.azure.com/",
    api_version="2023-12-01-preview", temperature=0.0
)

embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding",
    api_key="fb569c7a7f444edc82d434e58b525dd7",
    azure_endpoint="https://arogya-kys-ai.openai.azure.com/",
    api_version="2023-07-01-preview"
    
)


Settings.llm = llm
Settings.embed_model = embed_model
# Settings.callback_manager = CallbackManager([token_counter])


input_file_path = '/Users/sunilthakur/Downloads/Dietary_Guidelines_for_Americans-2020-2025.pdf'

documents = SimpleDirectoryReader(
    input_files=[input_file_path]
).load_data()
index = VectorStoreIndex.from_documents(documents)



query = "What's appropriate diet for 40 plus adult?"
query_engine = index.as_query_engine()
answer = query_engine.query(query)
print(answer.response)

while not query.lower() in ['quit', 'exit', 'end']:
    print('\nAsk your question \n')

    query = str(input())

    if not query.lower() in ['quit', 'exit', 'end']:

        result = query_engine.query(query)
        print(result)

        # update_context_pipeline = Pipeline()
        # update_context_pipeline.run()

    else:
        print('Ending your session')
# print(
#     "Embedding Tokens: ",
#     token_counter.total_embedding_token_count,
#     "\n",
#     "LLM Prompt Tokens: ",
#     token_counter.prompt_llm_token_count,
#     "\n",
#     "LLM Completion Tokens: ",
#     token_counter.completion_llm_token_count,
#     "\n",
#     "Total LLM Token Count: ",
#     token_counter.total_llm_token_count,
#     "\n",
# )