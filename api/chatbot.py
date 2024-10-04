'''
Created on Jul 18, 2024

@author: sunilthakur
'''

import mesop as me
import mesop.labs as mel
from mesop import stateclass

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage

from app.api.chatbot.components import icon_button
from app.api.chatbot.styles import _STYLE_CONFIG_HEADER
from app.api.chatbot.event_handlers import on_click_show_options

from app.api.chatbot.data_models import State

from app.api.ragchat import rag

@me.page(path="/", title="RAG Chat", stylesheets = ["https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"])
def page():
    
    # with me.box(style=_STYLE_CONFIG_HEADER):
    #     icon_button(
    #         icon="code", tooltip="Code", label="CODE", on_click=on_click_show_options
    #   )
        
    state = me.state(State)
    with me.sidenav(
        opened=state.sidenav_open, style=me.Style(width=200)
    ):
        me.text("Inside sidenav")
    
    with me.box(
        style=me.Style(
            margin=me.Margin(left=200 if state.sidenav_open else 0),
        ),
    ):
        with me.content_button(on_click=on_click_show_options):
            me.icon("menu")
            me.markdown("Main content")
                
    mel.chat(transform, title="RAG Chat", bot_user="Mycroft")
    
def transform(message: str, history: list[ChatMessage]):
    
    for resp in rag.stream_chat(message, history):
        yield resp
    
