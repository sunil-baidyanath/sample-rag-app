'''
Created on Jul 26, 2024

@author: sunilthakur
'''

import mesop as me

from app.api.chatbot.data_models import Role

# Constants

_TITLE = "RAG Chat"

_ROLE_USER = "user"
_ROLE_ASSISTANT = "assistant"

_BOT_USER_DEFAULT = "bot"
_USER_DEFAULT = "you"


def _make_modal_background_style(modal_open: bool) -> me.Style:
    """Makes style for modal background.
    
    Args:
    
    modal_open: Whether the modal is open.
    
    """
    return me.Style(
        display="block" if modal_open else "none",
        position="fixed",
        z_index=1000,
        width="100%",
        height="100%",
        overflow_x="auto",
        overflow_y="auto",
        background="rgba(0,0,0,0.4)",
    )


_DEFAULT_PADDING = me.Padding.all(15)
_DEFAULT_BORDER = me.Border.all(
  me.BorderSide(color="#e0e0e0", width=1, style="solid")
)

_STYLE_INPUT_WIDTH = me.Style(width="100%")
_STYLE_SLIDER_INPUT_BOX = me.Style(display="flex", flex_wrap="wrap")
_STYLE_SLIDER_WRAP = me.Style(flex_grow=1)
_STYLE_SLIDER_LABEL = me.Style(padding=me.Padding(bottom=10))
_STYLE_SLIDER = me.Style(width="90%")
_STYLE_SLIDER_INPUT = me.Style(width=75)

_STYLE_STOP_SEQUENCE_BOX = me.Style(display="flex")
_STYLE_STOP_SEQUENCE_WRAP = me.Style(flex_grow=1)

_STYLE_CONTAINER = me.Style(
  display="grid",
  grid_template_columns="5fr 2fr",
  grid_template_rows="auto 5fr",
  height="100vh",
)

_STYLE_MAIN_HEADER = me.Style(
  padding=me.Padding.all(15), display="flex", flex_direction="row", align_content="space-between",
)

_STYLE_MAIN_COLUMN = me.Style(
  border=_DEFAULT_BORDER,
  padding=me.Padding.all(15),
  overflow_y="scroll",
)

_STYLE_CONFIG_COLUMN = me.Style(
  border=_DEFAULT_BORDER,
  padding=me.Padding.all(15),
  overflow_y="scroll",
)

_STYLE_TITLE_BOX = me.Style(display="inline-block", width="100%", flex_grow=1)

_STYLE_CONFIG_HEADER = me.Style(
  border=_DEFAULT_BORDER, padding=me.Padding.all(10)
)

_STYLE_STOP_SEQUENCE_CHIP = me.Style(margin=me.Margin.all(3))

_STYLE_MODAL_CONTAINER = me.Style(
  background="#fff",
  margin=me.Margin.symmetric(vertical="0", horizontal="auto"),
  width="min(1024px, 100%)",
  box_sizing="content-box",
  height="100vh",
  overflow_y="scroll",
  box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
)

_STYLE_MODAL_CONTENT = me.Style(margin=me.Margin.all(30))

_STYLE_CODE_BOX = me.Style(
  font_size=13,
  margin=me.Margin.symmetric(vertical=10, horizontal=0),
  padding=me.Padding.all(10),
  border=me.Border.all(me.BorderSide(color="#e0e0e0", width=1, style="solid")),
)

_COLOR_BACKGROUND = "#f0f4f8"
_COLOR_CHAT_BUBBLE_YOU = "#f2f2f2"
_COLOR_CHAT_BUBBLE_BOT = "#ebf3ff"
_COLOR_CHAT_BUUBBLE_EDITED = "#f2ebff"

_DEFAULT_PADDING = me.Padding.all(20)
_DEFAULT_BORDER_SIDE = me.BorderSide(
  width="1px", style="solid", color="#ececec"
)

_LABEL_BUTTON = "send"
_LABEL_BUTTON_IN_PROGRESS = "pending"
_LABEL_INPUT = "Enter your prompt"

_STYLE_INPUT_WIDTH = me.Style(width="100%")

_STYLE_APP_CONTAINER = me.Style(
  background=_COLOR_BACKGROUND,
  display="grid",
  height="100vh",
  grid_template_columns="80px 1fr",
  # grid_template_columns="80px 1fr",
  # margin=me.Margin(left="auto", right="auto")
  width="min(1024px, 100%)",
  margin=me.Margin.symmetric(vertical=0, horizontal="auto"),
  box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
)
_STYLE_TITLE = me.Style(padding=me.Padding(left=10))
_STYLE_CHAT_BOX = me.Style(
  height="100%",
  overflow_y="scroll",
  padding=_DEFAULT_PADDING,
  margin=me.Margin(bottom=20),
  border_radius="10px",
  border=me.Border(
    left=_DEFAULT_BORDER_SIDE,
    right=_DEFAULT_BORDER_SIDE,
    top=_DEFAULT_BORDER_SIDE,
    bottom=_DEFAULT_BORDER_SIDE,
  ),
)
_STYLE_CHAT_INPUT = me.Style(width="100%")
_STYLE_CHAT_INPUT_BOX = me.Style(
  padding=me.Padding(top=30, bottom=30), display="flex", flex_direction="row", 
)
_STYLE_CHAT_BUTTON = me.Style(margin=me.Margin(top=8, left=8))
_STYLE_CHAT_BUBBLE_NAME = me.Style(
  font_weight="bold",
  font_size="12px",
  padding=me.Padding(left=15, right=15, bottom=5),
)
_STYLE_CHAT_BUBBLE_PLAINTEXT = me.Style(margin=me.Margin.symmetric(vertical=15))

_STYLE_MODAL_CONTAINER = me.Style(
  background="#fff",
  margin=me.Margin.symmetric(vertical="0", horizontal="auto"),
  width="min(1024px, 100%)",
  box_sizing="content-box",
  height="100vh",
  overflow_y="scroll",
  box_shadow=("0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"),
)

_STYLE_MODAL_CONTENT = me.Style(margin=me.Margin.all(20))

_STYLE_PREVIEW_CONTAINER = me.Style(
  display="grid",
  grid_template_columns="repeat(2, 1fr)",
)

_STYLE_PREVIEW_ORIGINAL = me.Style(color="#777", padding=_DEFAULT_PADDING)

_STYLE_PREVIEW_REWRITE = me.Style(
  background=_COLOR_CHAT_BUUBBLE_EDITED, padding=_DEFAULT_PADDING
)


def _make_style_chat_ui_container(has_title: bool) -> me.Style:
    """Generates styles for chat UI container depending on if there is a title or not.
    
    Args:
        has_title: Whether the Chat UI is display a title or not.
    """
    return me.Style(
        display="grid",
        grid_template_columns="repeat(1, 1fr)",
        grid_template_rows="1fr 14fr 1fr" if has_title else "5fr 1fr",
        # margin=me.Margin.symmetric(vertical=0, horizontal="auto"),
        # width="min(860px, 90%)",
        height="100vh",
        background="#fff",
        # box_shadow=(
        #   "0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"
        # ),
        padding=me.Padding(top=20, left=20, right=20),
    )


def _make_style_chat_bubble_wrapper(role: Role) -> me.Style:
    """Generates styles for chat bubble position.

    Args:
        role: Chat bubble alignment depends on the role
    """
    align_items = "end" if role == _ROLE_USER else "start"
    return me.Style(
        display="flex",
        flex_direction="row",
        align_items=align_items,
        justify_content=align_items,
    )


def _make_chat_bubble_style(role: Role, edited: bool) -> me.Style:
    """Generates styles for chat bubble.

    Args:
        role: Chat bubble background color depends on the role
        edited: Whether chat message was edited or not.
    """
    background = _COLOR_CHAT_BUBBLE_YOU
    left_margin = "auto"
    border_radius = "15px"
    if role == _ROLE_ASSISTANT:
        background = _COLOR_CHAT_BUBBLE_BOT
        left_margin = "0"
      
    else:
        background = _COLOR_CHAT_BUUBBLE_EDITED
        # left_margin = "0" 
        
    return me.Style(
        width="80%",
        font_size="16px",
        line_height="1.5",
        background=background,
        border_radius=border_radius,
        padding=me.Padding(right=15, left=15, bottom=3),
        margin=me.Margin(left=left_margin, bottom=10),
        border=me.Border(
          left=_DEFAULT_BORDER_SIDE,
          right=_DEFAULT_BORDER_SIDE,
          top=_DEFAULT_BORDER_SIDE,
          bottom=_DEFAULT_BORDER_SIDE,
        ),
    )

def _display_username(username: str, edited: bool = False) -> str:
    """Displays the username

    Args:
        username: Name of the user
        edited: Whether the message has been edited.
    """
    edited_text = " (edited)" if edited else ""
    return username + edited_text