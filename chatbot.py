'''
Created on Jul 26, 2024

@author: sunilthakur
'''

import mesop as me
import mesop.labs as mel

from app.api.chatbot.data_models import State, ChatMessage
from app.api.chatbot.components import modal, modal_window, chat_window, side_nav

from app.rag import RAGEngine, RAGSettings

setting = RAGSettings.configure()

rag_engine = RAGEngine('diets', setting)


@me.page(
  security_policy=me.SecurityPolicy(
    allowed_iframe_parents=["https://google.github.io"]
  ),
  path="/",
  title="RAG Chat",
  stylesheets = ["https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"]
)
def page():
    state = me.state(State)
    
    # with modal(modal_open=state.modal_open):
    #     modal_window()
    
    # with me.box(style=me.Style(
    #     # background=_BACKGROUND_COLOR,
    #     # color=_FONT_COLOR,
    #     display="grid",
    #     grid_template_columns="2fr 8fr",
    #     height="100vh",
    #   )):
    # side_nav()
    chat_window('RAG Chat', state, respond_to_chat)
   


def respond_to_chat(message: str, history: list[ChatMessage]):
    for resp in rag_engine.stream_chat(message, history):
        yield resp