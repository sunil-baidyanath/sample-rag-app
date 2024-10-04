import time
from typing import Callable, Generator, Literal

import mesop as me

from app.api.chatbot.data_models import State, ChatMessage

from app.api.chatbot.styles import (
    _STYLE_CODE_BOX, 
    _STYLE_MODAL_CONTAINER, 
    _STYLE_MODAL_CONTENT, 
    _STYLE_CONFIG_COLUMN, 
    _STYLE_INPUT_WIDTH, 
    _STYLE_APP_CONTAINER,
    _STYLE_CONFIG_HEADER, 
    _STYLE_MAIN_HEADER,
    _STYLE_TITLE_BOX,
    _STYLE_TITLE,
    _STYLE_CHAT_BOX,
    _STYLE_CHAT_BUBBLE_NAME,
    _STYLE_CHAT_BUBBLE_PLAINTEXT,
    _STYLE_CHAT_INPUT_BOX,
    _LABEL_INPUT,
    _STYLE_CHAT_INPUT,
    _STYLE_CHAT_BUTTON,
    _LABEL_BUTTON_IN_PROGRESS,
    _LABEL_BUTTON,
    _make_modal_background_style,
    _make_style_chat_ui_container, 
    _make_style_chat_bubble_wrapper, 
    _display_username,
    _make_chat_bubble_style
)

from app.api.chatbot.event_handlers import (
    on_click_modal, 
    on_click_show_modal,
    on_knowledgebase_select
)

_ROLE_USER = "user"
_ROLE_ASSISTANT = "assistant"
BACKGROUND_COLOR = "#e2e8f0"

def side_nav():
    def on_click_chat(e: me.InputEvent):
        """Capture chat text input."""
        # state = me.state(State)
        # state.input = e.value
        
    def on_click_index(e: me.InputEvent):
        """Capture chat text input."""
        # state = me.state(State)
        # state.input = e.value
        
    def on_click_history(e: me.InputEvent):
        """Capture chat text input."""
        # state = me.state(State)
        # state.input = e.value
        
    # with me.box(style=me.Style(display="flex", flex_direction="column", padding=me.Padding.all(1))):
    # # with me.sidenav(opened=True):
    #     # Toolbar
    with me.box(style=me.Style(width=80, padding=me.Padding(top=50, bottom=50, left=5, right=5),border=me.Border(bottom=me.BorderSide(width=1, style="solid", color="#bbb")),)):
        with me.box(style=me.Style(display="flex", flex_direction="column", align_content="space-between", height="100%")):
            with me.box(style=me.Style(display="flex", flex_direction="column", height="100%", flex_grow=1)):
                with me.content_button(on_click=on_click_chat):
                    with me.tooltip(message="Chat"):
                        me.icon(icon="chat")
                with me.content_button(on_click=on_click_index):
                    with me.tooltip(
                        message="Indexes" #if state.show_preview else "Show preview"
                    ):
                        me.icon(icon="database")
                with me.content_button(on_click=on_click_history):
                    with me.tooltip(
                        message="Chat History"
                    ):
                        me.icon(icon="history")
            with me.box(style=me.Style(display="flex", flex_direction="column")):
                with me.content_button(on_click=on_click_chat):
                    with me.tooltip(message="Settings"):
                        me.icon(icon="settings")

def chat_window(title: str, 
                state: State,
                transform: Callable[
                    [str, list[ChatMessage]], Generator[str, None, None] | str
                ]):
    
    def on_chat_input(e: me.InputEvent):
        """Capture chat text input."""
        state = me.state(State)
        state.input = e.value
      
    def on_click_submit_chat_msg(e: me.ClickEvent | me.InputEnterEvent):
        """Handles submitting a chat message."""
        print('coming to submit_chat_msg')
        state = me.state(State)
        print(state.in_progress)
        print(state.input)
        if state.in_progress or not state.input:
            return
        input = state.input
        
        state.input = ""
        yield
        
        output = state.output
        if output is None:
            output = []
        
        output.append(ChatMessage(role=_ROLE_USER, content=input))
        state.in_progress = True
        yield
    
        me.scroll_into_view(key="scroll-to")
        time.sleep(0.15)
        yield
        
        start_time = time.time()
        output_message = transform(input, state.output)
        assistant_message = ChatMessage(role=_ROLE_ASSISTANT)
        output.append(assistant_message)
        state.output = output
        for content in output_message:
            assistant_message.content += content
            # TODO: 0.25 is an abitrary choice. In the future, consider making this adjustable.
            if (time.time() - start_time) >= 0.25:
                start_time = time.time()
                yield
    
        state.in_progress = False
        yield     
  
    with me.box(style=_STYLE_APP_CONTAINER):
        side_nav()
        with me.box(style=_make_style_chat_ui_container(bool(title))):
            with me.box(style=_STYLE_MAIN_HEADER):
                with me.box(style=_STYLE_TITLE_BOX):
                    me.text(title, type="headline-6", style=_STYLE_TITLE)
            
                icon_button(
                    icon="menu", tooltip="Options", label="", on_click=on_click_show_modal
                )
            
            with me.box(style=_STYLE_CHAT_BOX):
                for index, msg in enumerate(state.output):
                    with me.box(
                        style=_make_style_chat_bubble_wrapper(msg.role),
                        key=f"msg-{index}",
                        
                    ):
                        # if msg.role == _ROLE_ASSISTANT:
                        #     me.text(
                        #         _display_username(_BOT_USER_DEFAULT, msg.edited),
                        #         style=_STYLE_CHAT_BUBBLE_NAME,
                        #     )
                        # else:
                        #     me.text(
                        #         _display_username(_USER_DEFAULT, msg.edited),
                        #         style=_STYLE_CHAT_BUBBLE_NAME,
                        #     )
                        with me.box(style=_make_chat_bubble_style(msg.role, msg.edited)):
                            if msg.role == _ROLE_USER:
                                me.text(msg.content, style=_STYLE_CHAT_BUBBLE_PLAINTEXT)
                            else:
                                me.text(msg.content, style=_STYLE_CHAT_BUBBLE_PLAINTEXT)
    
                if state.in_progress:
                    with me.box(key="scroll-to", style=me.Style(height=300)):
                        pass
                    
            # subtle_chat_input()
            with me.box(style=_STYLE_CHAT_INPUT_BOX):
                with me.content_button(
                    type="icon",
                    style=me.Style(margin=me.Margin(top=8,right=8)),
                ):
                    me.icon("add")
                    
                with me.box(style=me.Style(display="flex", flex_direction="row", width="100%", background="#e3e1ec", border_radius=16, padding=me.Padding.all(8))):
                    with me.box(style=me.Style(flex_grow=1)):
                        # me.input(
                        #     label=_LABEL_INPUT,
                        #     # Workaround: update key to clear input.
                        #     key=f"input-{len(state.output)}",
                        #     on_input=on_chat_input,
                        #     on_enter=on_click_submit_chat_msg,
                        #     style=_STYLE_CHAT_INPUT,
                        # )
                        me.native_textarea(
                            autosize=True,
                            min_rows=2,
                            placeholder="Enter your query",
                            style=me.Style(
                              padding=me.Padding(top=16, left=16),
                              background="#e3e1ec",
                              outline="none",
                              width="100%",
                              overflow_y="auto",
                              border=me.Border.all(
                                me.BorderSide(style="none"),
                              ),
                            ),
                            # Workaround: update key to clear input.
                            key=f"input-{len(state.output)}",
                            on_input=on_chat_input,
                            # on_enter=on_click_submit_chat_msg,
                        )
                    
                    with me.content_button(
                        type="icon",
                        style=_STYLE_CHAT_BUTTON,
                    ):
                        me.icon("upload")
            
                with me.content_button(
                    color="primary",
                    type="flat",
                    disabled=state.in_progress,
                    on_click=on_click_submit_chat_msg,
                    style=_STYLE_CHAT_BUTTON,
                ):
                    me.icon(
                        _LABEL_BUTTON_IN_PROGRESS if state.in_progress else _LABEL_BUTTON
                    ) 
            

    
        
@me.component
def modal_window():
    with me.box(style=_STYLE_CONFIG_COLUMN):
        with me.box():
            me.select(
            options=[
                me.SelectOption(label="Dietary Guidelines", value="dietary_guidelines"),
                me.SelectOption(label="Activity Guidelines", value="activity_guidelines"),
            ],
            label="Knowledgebase",
            style=_STYLE_INPUT_WIDTH,
            on_selection_change=on_knowledgebase_select,
            value='dietary_guidelines',
        )
        
        with me.box():
            me.select(
            options=[
                me.SelectOption(label="Professional Consultant", value="dietary_guidelines"),
                me.SelectOption(label="Friendly Advisor", value="activity_guidelines"),
            ],
            label="Persona",
            style=_STYLE_INPUT_WIDTH,
            on_selection_change=on_knowledgebase_select,
            value='dietary_guidelines',
        )
            
        with me.box():
            me.select(
            options=[
                # me.SelectOption(label="Dietary Guidelines", value="dietary_guidelines"),
                # me.SelectOption(label="Activity Guidelines", value="activity_guidelines"),
            ],
            label="Conversation Context",
            style=_STYLE_INPUT_WIDTH,
            on_selection_change=on_knowledgebase_select,
            value='dietary_guidelines',
        )
    
    me.button(label="Close", type="raised", on_click=on_click_modal)



@me.component
def icon_button(*, icon: str, label: str, tooltip: str, on_click: Callable):
    """Icon button with text and tooltip."""
    with me.content_button(on_click=on_click):
        with me.tooltip(message=tooltip):
            with me.box(style=me.Style(display="flex")):
                me.icon(icon=icon)
                me.text(
                    label, style=me.Style(line_height="24px", margin=me.Margin(left=5))
                )


@me.content_component
def modal(modal_open: bool):
    """Basic modal box."""
    with me.box(style=_make_modal_background_style(modal_open)):
        with me.box(style=_STYLE_MODAL_CONTAINER):
            with me.box(style=_STYLE_MODAL_CONTENT):
                me.slot()  
                
                
