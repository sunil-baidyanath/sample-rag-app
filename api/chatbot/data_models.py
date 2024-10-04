'''
Created on Jul 26, 2024

@author: sunilthakur
'''

import mesop as me
from dataclasses import dataclass

from typing import Literal

Role = Literal["user", "assistant"]

@dataclass(kw_only=True)
class ChatMessage:
    """Chat message metadata."""
    role: Role = "user"
    content: str = ""
    edited: bool = False

@me.stateclass
class State:
    input: str
    history: list[ChatMessage]
    in_progress: bool = False
    # Prompt / Response
    input: str
    response: str
    output: list[ChatMessage]
    # Tab open/close
    prompt_tab: bool = True
    response_tab: bool = True
    # Modal
    modal_open: bool = False
    # Workaround for clearing inputs
    clear_prompt_count: int = 0
    clear_sequence_count: int = 0
    #sidenav
    sidenav_open: bool


