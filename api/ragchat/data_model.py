'''
Created on Jul 20, 2024

@author: sunilthakur
'''
from llama_index.core.llms import ChatMessage

from dataclasses import dataclass, field
from typing import Literal
from enum import Enum

import mesop as me

Role = Literal["user", "model"]

# @dataclass(kw_only=True)
# class ChatMessage:
#     role: Role = "user"
#     content: str = ""
#     in_progress: bool = False

class Models(Enum):
    GEMINI_1_5_FLASH = "Gemini 1.5 Flash"
    GEMINI_1_5_PRO = "Gemini 1.5 Pro"
    CLAUDE_3_5_SONNET = "Claude 3.5 Sonnet"

@dataclass
class Conversation:
    model: str = ""
    messages: list[ChatMessage] = field(default_factory=list)

@me.stateclass
class State:
    input: str
    history: list[ChatMessage]
    in_progress: bool = False

@me.stateclass
class ModelDialogState:
    selected_models: list[str] = field(default_factory=list)