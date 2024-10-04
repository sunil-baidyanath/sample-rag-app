
'''
Step 1: Build the knowledgebase
Step 1.a: Extracting the relevant information
Step 1.b: Breaking the information into smaller chunks
Step 1.c: Create the embeddings and store in a vector database
Step 2: Setup chatbot orchestrator
Step 2.a: Create chatbot profile by setting up a prompt template
Step 2.b: Setup context for the conversation
Step 3: Process user query
Step 3.a: Convert the user query to its relevant embedding.
Step 3.b: Query the vector database for documents relevant to the query.
Step 3.4: Build the prompt for LLM.
Step 3.5: Pass the prompt to the LLM and get the response.
Step 4: Create a chain for invoking the LLM.
Step 5: Build API 
'''

from app.api.chatbot.core.context import ChatContext
from app.api.chatbot.core.kernel import ChatbotKernel

class Chatbot(object):
    
    def __init__(self):
        ChatbotKernel.get_instance().setup()
        self.context = ChatContext.load()
        
    
    def chat(self, message: str):
        pass
        