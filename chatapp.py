'''
Created on Jul 26, 2024

@author: sunilthakur
'''

import mesop as me
import mesop.labs as mel

from app.rag import RAGEngine, RAGSettings


setting = RAGSettings.configure()

rag_engine = RAGEngine('diets')


@me.page(
  security_policy=me.SecurityPolicy(
    allowed_iframe_parents=["https://google.github.io"]
  ),
  path="/",
  title="RAG Chat",
  stylesheets = ["https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"]
)
def page():
    mel.chat(respond_to_chat, title='RAG Chat')


def respond_to_chat(message: str, history: list[mel.ChatMessage]):
    for resp in rag_engine.stream_chat(message, history):
        yield resp