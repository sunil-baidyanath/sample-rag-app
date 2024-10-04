'''
Created on Feb 12, 2024

@author: sunilthakur
'''


import os
# from openai import AzureOpenAI
# from openai import AzureChatOpenAI

from langchain_openai import AzureChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate

    # Improvemets
    # 1. Efficient chunking: By breaking down the PDF document into smaller sections and processing them sequentially, we can bypass the token limit and extract information from the entire document seamlessly.
    # 2. Better retrieval algorithms: By breaking down the PDF document into smaller sections and processing them sequentially, we can bypass the token limit and extract information from the entire document seamlessly.
    # 3. Embeddings and vector databases: By integrating vector databases, we can speed up the retrieval process and ensure more accurate results. Converting the text in the PDF document and the query into numerical representations, we can measure the semantic similarity between them.
    # 4. allows users to input multiple questions and receive corresponding answers in a structured manner. This interface can support advanced query features like complex boolean operations, filters, and context-aware querying.
    
    # Steps
    # 1. Create vector index
    # 1.1. Load files from local or remote locations
    # 1.2. Parse and split the file into smaller chunks called documents
    # 1.3. Send the documents to Azure OpenAI to generate embedding vectors
    # 1.4. Create a vector index store, which allows for efficient organization and access to vector data
     
    # 2. Generate completions
    
DATA_PATH = '/Users/sunilthakur/Downloads/Dietary_Guidelines_for_Americans-2020-2025.pdf'
DB_FAISS_PATH = 'vectorstore/db_faiss'

def save_pdf_as_vector():
    
    loader = PyPDFLoader(DATA_PATH)

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                       model_kwargs={'device': 'cpu'})
    
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(DB_FAISS_PATH)
    
    
def init_chat_bot():
    
    AZURE_OPENAI_KEY = 'fb569c7a7f444edc82d434e58b525dd7'
    AZURE_OPENAI_ENDPOINT = 'https://arogya-kys-ai.openai.azure.com/'
    
    llm = AzureChatOpenAI(deployment_name='gpt-functions',
                      model_name='gtp-3.5-turbo',
                      azure_endpoint = AZURE_OPENAI_ENDPOINT,
                      openai_api_version='2023-12-01-preview',
                      openai_api_key=AZURE_OPENAI_KEY,
                      openai_api_type="azure")
    
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                        model_kwargs={'device': 'cpu'})
    
    vectorStore = FAISS.load_local(DB_FAISS_PATH, embeddings)
    
    
    retriever = vectorStore.as_retriever(search_type="similarity", search_kwargs={"k":2})
    
    # qa = ConversationalRetrievalChain.from_llm(llm=llm,
    #                                         retriever=retriever,
    #                                         condense_question_prompt=QUESTION_PROMPT,
    #                                         return_source_documents=True,
    #                                         verbose=False)
    
    custom_prompt_template = """Use the following pieces of information to answer the user's question.
                                If you don't know the answer, just say that you don't know, don't try to make up an answer.
                                
                                Context: {context}
                                Question: {question}
                                
                                Only return the helpful answer below and nothing else.
                                Helpful answer:
                                """
    
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type='stuff',
                                           retriever=retriever,
                                           return_source_documents=True,
                                           chain_type_kwargs={'prompt': prompt},
                                           verbose=False
                                           )
    
    
    print('Initialized the chatbot \n')
    
    return qa_chain
    
def start_chat_bot(): 
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    qa = init_chat_bot()
    
    query = ''
    
    while not query.lower() in ['quit', 'exit', 'end']:
        print('\nAsk your question \n')
        
        query = str(input())
        
        if not query.lower() in ['quit', 'exit', 'end']:
        
            with get_openai_callback() as cb:
                response = qa({'query': query})
                print(response) 
                print(cb)
        
        else:
            print('Ending your session')
    
    

# save_pdf_as_vector()
start_chat_bot()

